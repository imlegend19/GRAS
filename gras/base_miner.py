import concurrent.futures
import signal
from abc import ABCMeta, abstractmethod

from gras.errors import InvalidTokenError
from gras.github.structs.rate_limit import RateLimitStruct
from gras.utils import to_iso_format


class BaseMiner(metaclass=ABCMeta):
    """
    BaseMiner class to store parameters parsed by `ArgumentParse` and start the mining process
    """
    
    def __init__(self, args):
        self.interface = args.interface
        self.repo_owner = args.repo_owner
        self.repo_name = args.repo_name
        self.start_date = to_iso_format(args.start_date)
        self.end_date = to_iso_format(args.end_date)
        
        self.basic = args.basic
        self.basic_extra = args.basic_extra
        self.issue_tracker = args.issue_tracker
        self.commit = args.commit
        self.pull_tracker = args.pull_tracker
        
        self.dbms = args.dbms
        self.db_name = args.db_name
        self.db_username = args.db_username
        self.db_password = args.db_password
        self.db_output = args.db_output
        self.db_host = args.db_host
        self.db_port = args.db_port
        self.db_log = args.db_log
        
        self.animator = args.animator
        self.tokens = args.tokens
    
    def __getattr__(self, attr):
        return self.__dict__[attr]
    
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value
    
    @abstractmethod
    def _load_from_file(self, file):
        """
        :func: `abc.abstractmethod` to load the settings from a .cfg file and instantiate the
        :class:`gras.base_miner.BaseMiner` class.
        
        Args:
            file: The .cfg file where the settings are stored

        Returns:
            None
        """
        pass
    
    def load_from_file(self, path):
        self._load_from_file(path)
    
    @abstractmethod
    def dump_to_file(self, path):
        """
        Method to dump the :class:`gras.base_miner.BaseMiner` object to a .cfg (config) file
        
        Args:
            path: The path of the .cfg file to be dumped

        Returns:
            None

        """
        pass
    
    @abstractmethod
    def process(self):
        pass
    
    @abstractmethod
    def _connect_to_db(self):
        pass
    
    @staticmethod
    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    @staticmethod
    def __get_rate_limit(token):
        rate = RateLimitStruct(
            github_token=token
        ).process()
        
        return rate.remaining
    
    def get_next_token(self):
        rem_token = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            process = {executor.submit(self.__get_rate_limit, token): token for token in self.tokens}
            for future in concurrent.futures.as_completed(process):
                token = process[future]
                
                try:
                    remaining = future.result()
                except Exception as e:
                    raise InvalidTokenError(msg=str(e))
                
                rem_token.append((remaining, token))
        
        rem_token.sort(reverse=True, key=lambda x: x[0])
        return rem_token[0][1]
