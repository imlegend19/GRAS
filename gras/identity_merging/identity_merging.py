import re
import string

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
