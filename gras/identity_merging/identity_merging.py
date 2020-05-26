import csv
import itertools
import logging
import re
import sys
import unicodedata

import requests
from yandex.Translater import Translater, TranslaterError

from gras.base_miner import BaseMiner
from gras.errors import YandexError, YandexKeyError
from gras.identity_merging.utils import damerau_levenshtein, monge_elkan
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
    
    :param id_: ID allotted to the contributor (PRIMARY KEY of `contributors` table)
    :type id_: int
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
    
    def __init__(self, id_, login, name, email, location=None, is_anonymous=0):
        self.id_ = id_
        self.contributor_id = None

        self.original_login = login.strip() if login is not None else None
        self.original_name = name.strip() if name is not None else None
        self.original_email = email.strip() if email is not None else None

        self.login = self.normalize_unicode_to_ascii(login) if login is not None else None
        self.name = self.normalize_unicode_to_ascii(name) if name is not None else None
        self.location = self.normalize_unicode_to_ascii(location) if location is not None else None
        self.is_anonymous = is_anonymous

        if self.login is not None:
            if not self.login.strip():
                self.login = None

        if self.name is not None:
            if not self.name.strip():
                self.name = None

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
                else:
                    self.email = self.__get_email(email)
                    self.prefix = self.normalize_unicode_to_ascii(self.email.split("@")[0]).strip()
                    self.domain = self.normalize_unicode_to_ascii(self.email.split("@")[1].strip())

                    if self.domain.strip() == '':
                        self.domain = None

                    if self.prefix.strip() == '':
                        self.prefix = None
            else:
                self.email = None
                self.prefix = None
                self.domain = None
        else:
            self.email = None
            self.prefix = None
            self.domain = None
    
    @staticmethod
    def __is_english(s):
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True
    
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
        
        return self.sort_words(val) if val is not None else None
    
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


class IdentityMerging(BaseMiner):
    def __init__(self, args):
        super().__init__(args=args)
        
        self._engine, self._conn = self._connect_to_db()
        self.yandex_key = args.yandex_key
        self.anon_contributors = []
        self.non_anon_contributors = []
        
        if self.yandex_key:
            translator.set_key(self.yandex_key)
            translator.set_to_lang('en')
    
    def _load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass
    
    def process(self):
        res = self._conn.execute(
            """
            SELECT DISTINCT id, name, email
            FROM contributors
            WHERE is_anonymous=1
            """
        ).fetchall()
        
        for r in res:
            self.anon_contributors.append(Alias(
                id_=r[0],
                login=None,
                name=r[1],
                email=r[2],
                is_anonymous=1,
            ))
        
        res = self._conn.execute(
            """
            SELECT DISTINCT id, login, name, email, location
            FROM contributors
            WHERE is_anonymous=0
            """
        ).fetchall()
        
        for r in res:
            self.non_anon_contributors.append(Alias(
                id_=r[0],
                login=r[1],
                name=r[2],
                email=r[3],
                location=r[4],
                is_anonymous=0
            ))

        print(TOTAL_TRANSLATED)

        file = open("react-result.csv", "a")

        writer = csv.writer(file)
        writer.writerow(['id-1', 'login', 'name-email', 'id-2', 'login', 'name-email', 'score'])

        it = 1
        for pair in self.__generate_pairs(self.non_anon_contributors, self.non_anon_contributors):
            print(f"Ongoing Pair: {it}")
            self._dump_pair(writer=writer, pair=pair)
            it += 1

        file.close()
    
    def _dump_pair(self, writer, pair):
        c1: Alias = pair[0]
        c2: Alias = pair[1]
        score = self.__get_score(c1, c2)
        
        if score > 0.4:
            if score > 1:
                print(c1.login, c1.prefix, c2.login, c2.prefix, score)
            writer.writerow([c1.id_, c1.login, f"{c1.name} <{c1.email}>", c2.id_, c2.login,
                             f"{c2.name} <{c2.email}>", score])
    
    @staticmethod
    def __get_score(c1, c2, inverse=True):
        """
        Calculates the aggregate score for 2 strings.
        
        :param c1: Contributor 1
        :type c1: Alias
        :param c2: Contributor 2
        :type c2: Alias
        :param inverse: `True` if similarity between non-anonymous users, else `False`
        :type inverse: bool
        
        :return: Final score
        :rtype: int
        """
        name_name = max(damerau_levenshtein(c1.name, c2.name), monge_elkan(c1.name, c2.name))
        name_prefix = max(damerau_levenshtein(c1.name, c1.prefix), damerau_levenshtein(c1.prefix, c2.name))
        prefix_prefix = damerau_levenshtein(c1.prefix, c2.prefix)
        login_name = max(damerau_levenshtein(c1.login, c2.name), damerau_levenshtein(c1.name, c2.login))
        login_prefix = max(damerau_levenshtein(c1.login, c2.prefix), damerau_levenshtein(c1.prefix, c2.login))
        
        if inverse:
            login_login = damerau_levenshtein(c1.login, c2.login)
            return sum([name_name, name_prefix, prefix_prefix, login_name, login_prefix, login_login]) / 6
        else:
            return sum([name_name, name_prefix, prefix_prefix, login_name, login_prefix]) / 5
    
    @staticmethod
    def __generate_pairs(lst1, lst2):
        for ele in lst1:
            temp = list(itertools.product([ele], lst2))
            for pair in temp:
                if pair[0].id_ != pair[1].id_:
                    yield pair
