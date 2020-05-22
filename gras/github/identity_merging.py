import re
import string

import numpy as np

from gras.base_miner import BaseMiner

TERMS = ["jr", "junior", "senior", "sr", "2nd", "ii", "iii", "iv", "v", "vi", "dr", "mr", "mrs", "ms", "phd", "prof",
         "professor", "miss", "mx", "sir", "mme", "msgr", "md", "server", "fake", "none", "null", "anonymous",
         "support", "admin", "unknown", "root", "nobody", "ubuntu", "(no author)", "system", "<blank>", "user"]

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


class Alias:
    """
    Represents an alias of a contributor.
    
    :param id_: ID allotted to the contributor (PRIMARY KEY of `contributors` table)
    :type id_: int
    :param login: `login` of the contributor
    :type login: str
    :param name: `name` of the contributor
    :type name: str
    :param email: `email` of the contributor
    :type email: str or None
    :param location: `location` of the contributor
    :type location: str or None
    :param is_anonymous: whether the contributor is anonymous or not
    :type is_anonymous: bool
    """
    
    def __init__(self, id_, login, name, email, location, is_anonymous):
        self.id_ = id_
        self.contributor_id = None
        
        self.login = self.__normalise_str(login)
        self.name = self.__normalise_str(name)
        self.location = self.__normalise_str(location)
        self.is_anonymous = is_anonymous
        
        email = self.__get_email(email)
        
        if re.search(EMAIL_REGEX, email):
            if email.endswith("example.com") or email.endswith(".(none)"):
                self.email = None
                self.prefix = None
                self.domain = None
            else:
                self.email = self.__get_email(email)
                self.prefix = self.__normalise_str(self.email.split("@")[0]).strip()
                self.domain = self.email.split("@")[1].strip()
        else:
            self.email = None
            self.prefix = None
            self.domain = None
    
    @staticmethod
    def __normalise_str(str_):
        str_ = str_.strip().lower()
        str_ = str_.translate(str.maketrans("", "", string.punctuation)).replace("\\'", "")
        return " ".join([x for x in str_.split() if x not in TERMS]).strip()
    
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
    
    def _load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass
    
    def process(self):
        res = self._conn.execute(
            """
            SELECT DISTINCT email
            FROM contributors
            WHERE email IS NOT NULL
            """
        ).fetchall()
        
        s = set()
        for r in res:
            try:
                s.add(r[0].split("@")[1])
            except IndexError:
                print(r[0])
        
        for i in s:
            print(i)
    
    @staticmethod
    def normalised_levenshtein(s1, s2):
        """
        Calculate the Levenshtein distance (or Edit distance) of 2 strings. This is an efficient iterative
        implementation of the algorithm.
        
        :param s1: s1 string
        :type s1: str
        
        :param s2: s2 string
        :type s2: str
        
        :return: 1 - distance(s1, s2) / max(len(s1), len(s2))
        :rtype: float
        """
        
        if s1 == s2:
            return 1
        
        if len(s1) == 0 or len(s2) == 0:
            return 0
        
        m, n = len(s1), len(s2)
        
        v1 = np.zeros(n + 1)
        v2 = np.zeros(n + 1)
        
        for i in range(n + 1):
            v1[i] = i
        
        for i in range(m):
            v2[0] = i + 1
            for j in range(n):
                deletion_cost = v1[j + 1] + 1
                insertion_cost = v2[j] + 1
                
                if s1[i] == s2[j]:
                    substitution_cost = v1[j]
                else:
                    substitution_cost = v1[j] + 1
                
                v2[j + 1] = min(deletion_cost, insertion_cost, substitution_cost)
            
            v1, v2 = v2, v1
        
        return 1 - v1[n] / max(n, m)
    
    def jaro_winkler(self, s1, s2, scaling=0.1):
        m, n = len(s1), len(s2)
        shorter, longer = s1, s2
        
        if m > n:
            shorter, longer = longer, shorter
        
        mc1 = self._get_matching_characters(shorter, longer)
        mc2 = self._get_matching_characters(longer, shorter)
        
        if len(mc1) == 0 or len(mc2) == 0:
            score = 0
        else:
            score = (float(len(mc1)) / len(shorter) + float(len(mc2)) / len(longer) +
                     float(len(mc1) - self._transpositions(mc1, mc2)) / len(mc1)) / 3.0
        
        index_ = None
        
        if s1 == s2:
            index_ = -1
        elif not s1 or not s2:
            index_ = 0
        else:
            max_len = min(m, n)
            for i in range(max_len):
                if not s1[i] == s2[i]:
                    index_ = i
                    break
            
            if not index_:
                index_ = max_len
        
        if index_ == -1:
            cl = s1
        elif index_ == 0:
            cl = ''
        else:
            cl = s1[:index_]
        
        cl = min(len(cl), 4)
        return round((score + (scaling * cl * (1 - score))) * 100) / 100
    
    @staticmethod
    def _transpositions(s1, s2):
        return np.floor(len([(f, s) for f, s in zip(s1, s2) if not f == s]) / 2.0)
    
    @staticmethod
    def _get_matching_characters(s1, s2):
        common = []
        limit = np.floor(min(len(s1), len(s2)) / 2)
        
        for i, l in enumerate(s1):
            left, right = int(max(0, i - limit)), int(min(i + limit + 1, len(s2)))
            if l in s2[left:right]:
                common.append(l)
                s2 = s2[:s2.index(l)] + '*' + s2[s2.index(l) + 1:]
        
        return ''.join(common)