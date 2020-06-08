import csv
import itertools
import logging
import re
import sys
import unicodedata
from collections import namedtuple
import networkx as nx

import requests
from joblib import load
from numpy import isnan
from sklearn.ensemble import RandomForestClassifier
from yandex.Translater import Translater, TranslaterError

from gras.base_miner import BaseMiner
from gras.db.db_models import DBSchema
from gras.errors import YandexError, YandexKeyError
from gras.identity_merging.utils import (
    damerau_levenshtein as dl, gen_count_dict, gen_feature_vector, get_domain_extensions,
    monge_elkan
)
from gras.utils import exception_handler

logger = logging.getLogger("main")
translator = Translater()

TOTAL_TRANSLATED = 0
TERMS = ["jr", "junior", "senior", "sr", "2nd", "ii", "iii", "iv", "v", "vi", "dr", "mr", "mrs", "ms", "phd", "prof",
         "professor", "miss", "mx", "sir", "mme", "msgr", "md", "server", "fake", "none", "null", "anonymous",
         "support", "admin", "unknown", "root", "nobody", "ubuntu", "(no author)", "system", "<blank>", "user",
         "noreplycom"]

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


class Alias:
    """
    Represents an alias of a contributor.

    :param contributor_id: ID allotted to the contributor (PRIMARY KEY of `contributors` table)
    :type contributor_id: int or None
    :param login: `login` of the contributor
    :type login: str or None
    :param name: `name` of the contributor
    :type name: str or None
    :param email: `email` of the contributor
    :type email: str or None
    :param location: `location` of the contributor
    :type location: str or None
    :param is_anonymous: whether the contributor is anonymous or not
    :type is_anonymous: int
    """

    def __init__(self, id_, contributor_id, login, name, email, extensions, location=None, is_anonymous=0):
        self.id_ = id_
        self.contributor_id = contributor_id

        self.original_login = login.strip().lower() if login is not None else None
        self.original_name = name.strip().lower() if name is not None else None
        self.original_email = email.strip().lower() if email is not None else None

        self.login = self.normalize_unicode_to_ascii(login) if login is not None else None
        self.name = self.normalize_unicode_to_ascii(name) if name is not None else None
        self.location = self.normalize_unicode_to_ascii(location) if location is not None else None
        self.is_anonymous = is_anonymous

        self.first_name = None
        self.last_name = None

        if self.login is not None:
            if not self.login.strip():
                self.login = None

        if self.name is not None:
            if not self.name.strip():
                self.name = None
            else:
                self.first_name = name.split()[0].lower()
                self.last_name = name.split()[-1].lower()

        if self.location is not None:
            if not self.location.strip():
                self.location = None

        email = self.__get_email(email) if email is not None else None

        if email:
            if re.search(EMAIL_REGEX, email):
                if email.endswith("example.com") or email.endswith(".(none)"):
                    self.email = None
                    self.prefix = None
                    self.domain = None
                    self.domain_ref = None
                else:
                    self.email = self.__get_email(email)
                    self.prefix = self.normalize_unicode_to_ascii(self.email.split("@")[0]).replace(' ', '').strip()
                    self.domain = self.email.split("@")[1].lower().strip()

                    if self.domain.strip() == '':
                        self.domain = None
                        self.domain_ref = None
                    else:
                        self.domain_ref = self.__refactor_domain(self.domain, extensions)

                    if self.prefix.strip() == '':
                        self.prefix = None
            else:
                self.email = None
                self.prefix = None
                self.domain = None
                self.domain_ref = None
        else:
            self.email = None
            self.prefix = None
            self.domain = None
            self.domain_ref = None

    @staticmethod
    def __is_english(s):
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    @staticmethod
    def __refactor_domain(domain, extensions):
        tokens = domain.split('.')
        new_domain = " ".join([x for x in tokens if x not in extensions])
        return new_domain

    @staticmethod
    def sort_words(words):
        words = sorted(words.split(" "))
        new_string = " ".join([x for x in words if x not in TERMS])
        return new_string

    @staticmethod
    @exception_handler(exceptions_to_catch=requests.ConnectionError, exception_to_raise=YandexError,
                       msg="Connection Error!")
    def translate():
        return translator.translate()

    def normalize_unicode_to_ascii(self, data):
        global TOTAL_TRANSLATED
        if not self.__is_english(data) and translator.key:
            TOTAL_TRANSLATED += 1

            logger.debug(f"Translating {data}...")
            translator.set_text(data)

            try:
                data = self.translate()
            except TranslaterError as e:
                if 'Forbidden' in e:
                    raise YandexKeyError(msg="Please enter a valid key.")
                else:
                    logger.error(f"Some error occurred in translating! Error: {e}")
                    sys.exit(1)

        normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
        val = normal.decode("utf-8").lower()
        val = re.sub('[^A-Za-z0-9 ]+', ' ', val)
        val = re.sub(' +', ' ', val)

        if not val.strip():
            val = None

        return self.sort_words(val).strip().lower() if val is not None else None

    @staticmethod
    def __get_email(str_):
        str_ = str_.strip().lower()

        if '[' in str_:
            # user[at]gmail[dot]com
            str_ = str_.replace('[at]', '@').replace('[dot]', '.')
        else:
            # user AT gmail dot com
            str_lst = str_.split()
            if len(str_lst) > 1:
                if 'dot' in str_lst:
                    str_lst[str_lst.index('dot')] = '.'

                if 'at' in str_lst:
                    ind = str_lst.index('at')
                    str_lst[ind] = '@'

                    # maiz at lulk in
                    if len(str_lst[ind + 1:]) > 1:
                        str_lst.append(str_lst[-1])
                        str_lst[-2] = '.'

                    # user at gmail
                    if '.' not in str_lst:
                        str_lst.append('.com')

            str_ = "".join(str_lst)

        return str_

    def __str__(self):
        return f"({self.original_login}, {self.original_name}, {self.original_email})"

    @property
    def dataset_str(self):
        return [self.id_, self.original_login, f"{self.original_name} <{self.original_email}>"]


class IdentityMiner(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)

        self._engine, self._conn = self._connect_to_db()

        self.db_schema = DBSchema(conn=self._conn, engine=self._engine)
        self.db_schema.create_tables()

        self.yandex_key = args.yandex_key
        self.anon_contributors = []
        self.non_anon_contributors = []

        # TODO: The statement is for sqlite, do for other db's
        self._conn.execute("PRAGMA foreign_keys=ON")

        if self.yandex_key:
            translator.set_key(self.yandex_key)
            translator.set_to_lang('en')

    def load_from_file(self, file):
        pass

    def dump_to_file(self, path):
        pass

    def __init_contributor_id(self):
        self._conn.execute(
            """
            UPDATE contributors
            SET contributor_id = id
            WHERE contributor_id IS NULL;
            """
        )

    def __update_contributors(self, cluster):
        min_id = min(cluster)

        for id_ in cluster:
            if id_ == min_id:
                pass
            else:
                self._conn.execute(
                    f"""
                    UPDATE contributors
                    SET contributor_id = {min_id}
                    WHERE contributor_id = {id_}
                    """
                )

    def refactor_contributors(self, field):
        res = self._conn.execute(
            f"""
            SELECT t.contributor_id, c.contributor_id
            FROM contributors t
            INNER JOIN (
                SELECT contributor_id, {field}
                FROM contributors
            ) c
            ON t.contributor_id != c.contributor_id AND t.{field} like c.{field}
            """
        ).fetchall()

        index = 0
        cont_index = {}
        for tup in res:
            if tup[0] in cont_index and tup[1] in cont_index:
                pass
            elif tup[0] not in cont_index and tup[1] in cont_index:
                cont_index[tup[0]] = cont_index[tup[1]]
            elif tup[0] in cont_index and tup[1] not in cont_index:
                cont_index[tup[1]] = cont_index[tup[0]]
            else:
                cont_index[tup[0]] = index
                cont_index[tup[1]] = index
                index += 1

        clusters = {}
        for k, v in cont_index.items():
            clusters.setdefault(v, []).append(k)

        print(clusters)
        logger.info("Updating contributors...")
        for clu in clusters.values():
            self.__update_contributors(clu)

    def __delete_contributor(self, id_):
        logger.debug(f"Deleting contributor {id_}...")
        self._conn.execute(
            f"""
            DELETE FROM contributors
            WHERE id={id_}
            """
        )

    def _delete_duplicates(self):
        Contributor = namedtuple("Contributor", ["login", "name", "email"])
        cont_id = {}

        res = self._conn.execute(
            f"""
            SELECT min(id), login, name, email
            FROM contributors
            GROUP BY login, name, email
            HAVING COUNT(*) > 1
            """
        ).fetchall()

        for row in res:
            cont_id[Contributor(login=row[1], name=row[2], email=row[3])] = row[0]

        res = self._conn.execute(
            f"""
            SELECT tc.id, tc.login, tc.name, tc.email
            FROM (
                SELECT dup, t.id, t.login, t.name, t.email
                FROM contributors t
                INNER JOIN (
                    SELECT id, RANK() OVER (PARTITION BY login, name, email ORDER BY id) AS dup
                    FROM contributors
                ) c
                ON t.id = c.id
            ) AS tc
            WHERE dup > 1;
            """
        ).fetchall()

        for row in res:
            self.__update_contributors([row[0], cont_id[Contributor(login=row[1], name=row[2], email=row[3])]])
            self.__delete_contributor(id_=row[0])

    def make_dataset(self, lst1, lst2):
        file = open(f"{self.repo_name}-result.csv", "a")

        writer = csv.writer(file)
        writer.writerow(['id-1', 'login', 'name-email', 'id-2', 'login', 'name-email', 'score'])

        it = 1
        for pair in self.__generate_pairs(lst1, lst2):
            print(f"Ongoing Pair: {it}")
            self._dump_pair(writer=writer, pair=pair)
            it += 1

        file.close()

    def make_dataset_using_model(self, model_path):
        users = set(self.anon_contributors).union(self.non_anon_contributors)
        prefix_count, domain_count, first_count, last_count = gen_count_dict(users)

        model: RandomForestClassifier = load(model_path)

        file = open("node_matches.csv", "a")
        writer = csv.writer(file)
        writer.writerow(['login', 'name-email', 'login', 'name-email'])

        for pair in self.__generate_pairs(self.non_anon_contributors, self.non_anon_contributors):
            if pair[0].contributor_id != pair[1].contributor_id:
                fv = gen_feature_vector(c1=pair[0], c2=pair[1], prefix_count=prefix_count, domain_count=domain_count,
                                        first_count=first_count, last_count=last_count)

                fv = [x if not isnan(x) else -1 for x in fv]

                result = model.predict([fv])[0]

                if result == 1:
                    writer.writerow([pair[0].login, f"{pair[0].name} <{pair[0].email}>", pair[1].login,
                                     f"{pair[1].name} <{pair[1].email}>"])

        file.close()

    def init_contributors(self):
        extensions = get_domain_extensions(path="/home/mahen/PycharmProjects/GRAS/gras/identity_merging/data"
                                                "/domain_ext.csv")

        res = self._conn.execute(
            """
            SELECT DISTINCT id, contributor_id, name, email
            FROM contributors
            WHERE is_anonymous=1
            """
        ).fetchall()

        for r in res:
            alias = Alias(
                id_=r[0],
                contributor_id=r[1],
                login=None,
                name=r[2],
                email=r[3],
                is_anonymous=1,
                extensions=extensions
            )

            self.anon_contributors.append(alias)

        res = self._conn.execute(
            """
            SELECT DISTINCT id, contributor_id, login, name, email, location
            FROM contributors
            WHERE is_anonymous=0
            """
        ).fetchall()

        for r in res:
            alias = Alias(
                id_=r[0],
                contributor_id=r[1],
                login=r[2],
                name=r[3],
                email=r[4],
                location=r[5],
                is_anonymous=0,
                extensions=extensions
            )

            self.non_anon_contributors.append(alias)

        logger.info(f"Total Translated: {TOTAL_TRANSLATED}")

    @staticmethod
    def evaluate_fields(f1, f2):
        if f1 is not None and f2 is not None:
            return f1 == f2
        else:
            return False

    def generate_exact_matches(self):
        file = open(f"{self.repo_name}_matches.csv", "a")
        writer = csv.writer(file)
        writer.writerow(['id', 'login', 'name-email', 'id', 'login', 'name-email'])

        for pair in self.__generate_pairs(self.anon_contributors, self.non_anon_contributors):
            lst = []
            if self.evaluate_fields(pair[0].login, pair[1].login) or self.evaluate_fields(pair[0].email, pair[1].email):
                # same
                lst.extend(pair[0].dataset_str)
                lst.extend(pair[1].dataset_str)
                print("CASE 1:", str(pair[0]), str(pair[1]))
            elif self.evaluate_fields(pair[0].prefix, pair[1].prefix):
                # slightly ambiguous
                lst.extend(pair[0].dataset_str)
                lst.extend(pair[1].dataset_str)
                print("CASE 2:", str(pair[0]), str(pair[1]))
            elif self.evaluate_fields(pair[0].login, pair[1].prefix) or \
                    self.evaluate_fields(pair[0].login, pair[1].domain) or \
                    self.evaluate_fields(pair[0].prefix, pair[1].login) or \
                    self.evaluate_fields(pair[0].domain, pair[1].login):
                # slightly ambiguous
                lst.extend(pair[0].dataset_str)
                lst.extend(pair[1].dataset_str)
                print("CASE 3:", str(pair[0]), str(pair[1]))
            elif self.evaluate_fields(pair[0].name, pair[1].prefix) or \
                    self.evaluate_fields(pair[0].name, pair[1].domain) or \
                    self.evaluate_fields(pair[0].prefix, pair[1].name) or \
                    self.evaluate_fields(pair[0].domain, pair[1].name):
                # slightly ambiguous
                lst.extend(pair[0].dataset_str)
                lst.extend(pair[1].dataset_str)
                print("CASE 4:", str(pair[0]), str(pair[1]))
            elif self.evaluate_fields(pair[0].name, pair[1].login) or \
                    self.evaluate_fields(pair[0].login, pair[1].name) or \
                    self.evaluate_fields(pair[0].name, pair[1].name):
                lst.extend(pair[0].dataset_str)
                lst.extend(pair[1].dataset_str)
                print("CASE 5:", str(pair[0]), str(pair[1]))

            if lst:
                writer.writerow(lst)

        file.close()

    def evaluate_exact_matches(self):
        file = open(f"{self.repo_name}_matches.csv")
        reader = csv.reader(file)

        edges = set()
        for row in reader:
            if reader.line_num == 1:
                continue

            if int(row[-1]) == 1:
                edges.add((int(row[0]), int(row[3])))

        graph = nx.Graph()
        graph.add_edges_from(list(edges))

        for cluster in nx.connected_components(graph):
            print(tuple(cluster))
            lst = []
            for id_ in cluster:
                res = self._conn.execute(
                    f"""
                    SELECT contributor_id
                    FROM contributors
                    WHERE id={id_}
                    """
                ).fetchone()

                lst.append(res[0])

            self.__update_contributors(lst)

    def process(self):
        # self.__init_contributor_id()
        #
        # self._delete_duplicates()
        #
        # logger.info("Forming exact contributor clusters...")
        # self.refactor_contributors(field='login')
        # self.refactor_contributors(field='email')

        self.init_contributors()
        self.evaluate_exact_matches()

    def _dump_pair(self, writer, pair):
        c1: Alias = pair[0]
        c2: Alias = pair[1]
        score = self.__get_score(c1, c2)

        if score > 0.3:
            writer.writerow([c1.contributor_id, c1.login, f"{c1.name} <{c1.email}>", c2.contributor_id, c2.login,
                             f"{c2.name} <{c2.email}>", score])

    @staticmethod
    def __get_score(c1, c2, inverse=True):
        """
        Calculates the aggregate score for 2 Aliases.

        :param c1: Contributor 1
        :type c1: Alias
        :param c2: Contributor 2
        :type c2: Alias
        :param inverse: `True` if similarity between non-anonymous users, else `False`
        :type inverse: bool

        :return: Final score
        :rtype: int
        """
        name_name = max(dl(c1.name, c2.name), monge_elkan(c1.name, c2.name))
        name_prefix = max(dl(c1.name, c1.prefix), dl(c1.prefix, c2.name))
        prefix_prefix = dl(c1.prefix, c2.prefix)
        login_name = max(dl(c1.login, c2.name), dl(c1.name, c2.login))
        login_prefix = max(dl(c1.login, c2.prefix), dl(c1.prefix, c2.login))

        if inverse:
            login_login = dl(c1.login, c2.login)
            return sum([name_name, name_prefix, prefix_prefix, login_name, login_prefix, login_login]) / 6
        else:
            return sum([name_name, name_prefix, prefix_prefix, login_name, login_prefix]) / 5

    @staticmethod
    def __generate_pairs(lst1, lst2):
        for ele in lst1:
            temp = list(itertools.product([ele], lst2))
            for pair in temp:
                if pair[0].contributor_id != pair[1].contributor_id:
                    yield pair
