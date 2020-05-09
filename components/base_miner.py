from abc import ABCMeta, abstractmethod

from components.utils import to_iso_format


class BaseMiner(metaclass=ABCMeta):
    """
    BaseMiner class to store parameters parsed by `ArgumentParse` and start the mining process
    """
    
    def __init__(self, args):
        self.interface = args.interface
        self.start_date = to_iso_format(args.start_date)
        self.end_date = to_iso_format(args.end_date)
        self.animator = args.animator
        self.dbms = args.dbms
        self.db_name = args.db_name
        self.db_username = args.db_username
        self.db_password = args.db_password
        self.db_output = args.db_output
        self.host = args.db_host
        self.port = args.db_port
        self.username = args.db_username
        self.repo_owner = args.repo_owner
        self.repo_name = args.repo_name
        self.token = args.token
        self.db_log = args.db_log
    
    def __getattr__(self, attr):
        return self.__dict__[attr]
    
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value
    
    @abstractmethod
    def _load_from_file(self, file):
        """
        :func: `abc.abstractmethod` to load the settings from a .cfg file and instantiate the
        :class:`components.base_miner.BaseMiner` class.
        
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
        Method to dump the :class:`components.base_miner.BaseMiner` object to a .cfg (config) file
        
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
