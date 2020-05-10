import argparse
import configparser
import getpass
import json
import logging.config
import os
import shutil
import sys
import threading
import time
from datetime import datetime
from queue import Queue

from gras.errors import GrasArgumentParserError, GrasConfigError
from gras.github.github_miner import GithubMiner
from gras.github.github_repo_stats import RepoStatistics
from gras.utils import ANIMATORS, DEFAULT_END_DATE, DEFAULT_START_DATE, to_iso_format
from local_settings import AUTH_KEY

LOGFILE = os.getcwd() + '/logs/{0}.{1}.log'.format(
    os.path.basename(__file__),
    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

DEFAULT_LOGGING = {
    'version'                 : 1,
    "disable_existing_loggers": False,
    "formatters"              : {
        "simple": {
            "format" : "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%d/%m/%Y %H:%M:%S"
        }
    },
    'handlers'                : {
        'console': {
            'class'    : 'logging.StreamHandler',
            'formatter': 'simple',
            'level'    : 'DEBUG',
            'stream'   : sys.stdout,
        },
        'file'   : {
            'class'    : 'logging.FileHandler',
            'formatter': 'simple',
            'level'    : 'DEBUG',
            'filename' : LOGFILE,
            'mode'     : 'w',
        },
    },
    'loggers'                 : {
        "main": {
            'level'    : 'DEBUG',
            'handlers' : ['console', 'file'],
            'propagate': False,
        },
    }
}


def set_up_logging():
    logging.basicConfig(level=logging.ERROR)
    logging.config.dictConfig(DEFAULT_LOGGING)


def get_repo_stats(args, repo_list=None):
    if repo_list:
        # repo_list: (owner, name, start_date, end_date)
        pass
    else:
        repo_stats = RepoStatistics(
            token=args.token,
            name=args.repo_name,
            owner=args.repo_owner,
            start_date=to_iso_format(args.start_date),
            end_date=to_iso_format(args.end_date)
        )
        
        return repo_stats.repo_stats()


def animated_loading(msg, animator):
    chars = animator
    
    for char in chars:
        sys.stdout.write('\r' + f"{msg}: " + char + "\t")
        time.sleep(.2)
        sys.stdout.flush()


def get_logging_level(level):
    choices = {
        'DEBUG'   : logging.DEBUG,
        'INFO'    : logging.INFO,
        'WARNING' : logging.WARNING,
        'ERROR'   : logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    return choices[level]


class GrasArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(
            description='GRAS - GIT REPOSITORIES ARCHIVING SERVICE',
            add_help=False
        )
        
        self._init_groups()
        self._add_gras_commands()
        self._add_grass_settings()
        self._add_database_settings()
        self._add_other_arguments()
        
        try:
            self.args = self.parse_args(['--stats', '-RO', 'sympy', '-RN', 'sympy', '-t', AUTH_KEY])
        except Exception as e:
            logger.error(e)
            sys.exit(1)
        
        if self.args.db_password:
            self.args.db_password = getpass.getpass('Enter Password: ')
        
        if self.args.config:
            self._read_config()
        
        self._set_arg_groups()
        self._validate()
        self._execute()
    
    @property
    def action_groups(self):
        return self._action_groups
    
    def _init_groups(self):
        self.gras_commands = self.add_argument_group('GRAS-COMMANDS')
        self.gras_settings = self.add_argument_group('GRAS-SETTINGS')
        self.database_settings = self.add_argument_group('DATABASE-SETTINGS')
        self.other = self.add_argument_group('OTHER')
    
    def _add_gras_commands(self):
        self.gras_commands.add_argument('-s', '--stats', help="View the stats of the repository", default=False,
                                        type=bool, const=True, nargs='?')
        self.gras_commands.add_argument('-g', '--generate', help="Generate a config file template", default=False,
                                        type=bool, const=True, nargs='?')
        self.gras_commands.add_argument('-m', '--mine', help="Mine the repository", default=False, type=bool,
                                        const=True, nargs='?')
    
    def _add_grass_settings(self):
        self.gras_settings.add_argument('-t', '--token', help="Personal API Access Token for parsing")
        self.gras_settings.add_argument('-i', '--interface', help="Interface of choice", default='github',
                                        choices=['github'], required=False)
        self.gras_settings.add_argument('-RO', '--repo-owner', help="Owner of the repository")
        self.gras_settings.add_argument('-RN', '--repo-name', help="Name of the repository")
        self.gras_settings.add_argument('-SD', '--start-date',
                                        help="Start Date for mining the data (in any ISO 8601 format, e.g., "
                                             "'YYYY-MM-DD HH:mm:SS +|-HH:MM')", default=DEFAULT_START_DATE,
                                        required=False)
        self.gras_settings.add_argument('-ED', '--end-date',
                                        help="End Date for mining the data (in any ISO 8601 format, e.g., 'YYYY-MM-DD "
                                             "HH:mm:SS +|-HH:MM')", default=DEFAULT_END_DATE, required=False)
        self.gras_settings.add_argument('-c', '--config', help="Path to the config file")
    
    def _add_database_settings(self):
        self.database_settings.add_argument('-dbms', help="DBMS to dump the data into", default='mysql',
                                            choices=["sqlite", "mysql", "postgresql"])
        self.database_settings.add_argument('-DB', '--db-name', help="Name of the database", default='gras')
        self.database_settings.add_argument('-U', '--db-username', help="The user name that is used to connect and "
                                                                        "operate the selected database")
        self.database_settings.add_argument('-P', '--db-password', help="The password for the user name entered",
                                            const=True, nargs='?')
        self.database_settings.add_argument('-H', '--db-host', help="The database server IP address or DNS name",
                                            default="localhost")
        self.database_settings.add_argument('-p', '--db-port',
                                            help="The database server port that allows communication to your "
                                                 "database", default=3306, type=int)
        self.database_settings.add_argument('-dbo', '--db-output',
                                            help="The path to the .db file in case of sqlite dbms")
        self.database_settings.add_argument('-dbl', '--db-log', help="DB-log flag to log the generated SQL produced",
                                            default=False, type=bool, nargs='?', required=False, const=True)
    
    def _add_other_arguments(self):
        self.other.add_argument("-h", "--help", action="help", help="show this help message and exit")
        self.other.add_argument('-a', '--animator', help="Loading animator", default='bar',
                                choices=list(ANIMATORS.keys()), required=False)
        self.other.add_argument('-OP', '--operation',
                                help="Choose the operation to perform for retrieving the stats.: 1. CREATE, 2. UPDATE, "
                                     "3. APPEND", choices=['1', '2', '3'], default='1')
        self.other.add_argument('-CL', '--clear-logs', help="Clear the logs directory", const=True, type=bool,
                                nargs='?', default=False)
        self.other.add_argument('-o', '--output', help="The output path where the config file is to be generated",
                                default=f"{os.getcwd()}/gras.ini")
    
    def _validate(self):
        args = self.args
        
        if (args.stats and args.generate) or (args.stats and args.mine) or (args.generate and args.mine):
            raise GrasArgumentParserError(msg="Only one GRAS command should be passed.")
        
        if args.generate:
            if not args.output:
                logger.info(f"Output path not provided, using default: {os.getcwd()}/gras.ini")
        
        if args.stats or args.mine:
            if not args.token:
                raise GrasArgumentParserError(msg="Please provide the token!")
            
            if not args.start_date:
                logger.info(f"Start date not provided, using default start date: {DEFAULT_START_DATE}.")
            
            if not args.end_date:
                logger.info(f"End data not provided, using default end date: {DEFAULT_END_DATE}.")
            
            if not args.repo_name or not args.repo_owner:
                if not args.config:
                    raise GrasArgumentParserError(msg="Either Repo-name and Repo-owner or GrasConfig file should "
                                                      "be provided!")
        
        if args.mine:
            if args.dbms == "sqlite" and not args.db_output:
                logger.info(f"SQLite database output file path not provided, using path: {os.getcwd()}/gras.db")
            
            if not args.username or not args.password:
                raise GrasArgumentParserError(msg="Please enter valid database credentials.")
            
            if args.username and args.password and not args.db_name:
                logger.info("Database name not provided! GRAS will create the database with name `gras` if not exists.")
            
            if not args.basic and not args.issue_tracker and not args.commit and not args.all:
                logger.info("Stage name not specified, using `basic` by default.")
    
    def _set_arg_groups(self):
        self.arg_groups = {}
        
        for group in self.action_groups:
            group_dict = {a.dest: getattr(self.args, a.dest, None) for a in group._group_actions}
            self.arg_groups[group.title] = argparse.Namespace(**group_dict)
    
    def _execute(self):
        if self.args.clear_logs:
            folder = os.path.dirname(LOGFILE)
            
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        
        if self.args.generate:
            self._create_config()
        
        if self.args.stats:
            try:
                repo_list = self.repo_list
            except AttributeError:
                repo_list = None
            
            queue = Queue()
            t = threading.Thread(name='process', target=lambda q, arg1, arg2: q.put(get_repo_stats(arg1, arg2)),
                                 args=(queue, self.args, repo_list))
            t.daemon = True
            t.start()
            
            now = datetime.now().strftime('%d/%d/%Y %H:%M:%S')
            
            while t.isAlive():
                animated_loading(f"{now} - main - INFO - Fetching `{self.args.repo_name}` statistics", ANIMATORS[
                    self.args.animator])
            
            t.join()
            result = queue.get()
            
            print("\n\n", "=" * 100, "\n", json.dumps(result, indent=4, sort_keys=True), "\n", "=" * 100)
        
        if self.args.mine:
            # TODO: Implement stages
            if self.args.interface == "github":
                gm = GithubMiner(args=self.args)
                gm.process()
            else:
                pass
    
    def _create_config(self):
        cfg = configparser.RawConfigParser()
        
        groups = {k: v for k, v in self.arg_groups.items() if k not in ['positional arguments', 'optional arguments']}
        
        for group in groups:
            if group == "GRAS-COMMANDS":
                continue
            
            cfg.add_section(group)
            group_dict = vars(groups[group])
            for key in group_dict:
                if key == "db_password":
                    cfg.set(group, key, "False  # should be entered on prompt")
                elif key == "config":
                    pass
                else:
                    cfg.set(group, key, group_dict[key])
        
        start_date = cfg.get('GRAS-SETTINGS', 'start_date') or DEFAULT_START_DATE
        end_date = cfg.get('GRAS-SETTINGS', 'end_date') or DEFAULT_END_DATE
        
        cfg.add_section('REPOSITORY-LIST')
        cfg.set('REPOSITORY-LIST', 'python/cpython', f'{start_date}, {end_date}')
        cfg.set('REPOSITORY-LIST', 'Microsoft/vscode', f', {end_date}')
        cfg.set('REPOSITORY-LIST', 'apache/spark', '')
        
        path = self.args.output
        
        try:
            with open(path, 'w') as file:
                cfg.write(file)
        except Exception as e:
            logger.error(e)
            sys.exit(1)
    
    def _read_config(self):
        cfp = configparser.ConfigParser()
        cfp.read(self.args.config)
        
        if cfp.has_section("REPOSITORY-LIST"):
            section = "REPOSITORY-LIST"
            
            repos = []
            
            try:
                for key in cfp[section]:
                    key = cfp[section][key].split('/')
                    value = cfp[section][key].split(',')
                    
                    if value[0] is None:
                        value[0] = DEFAULT_START_DATE
                    
                    if value[1] is None:
                        value[1] = DEFAULT_END_DATE
                    
                    repos.append((key[0], key[1], value[0], value[1]))
            except Exception:
                raise GrasConfigError(msg="Please check REPOSITORY-LIST section.")
            
            self.repo_list = repos
        
        if cfp.has_section("GRAS-SETTINGS"):
            section = "GRAS-SETTINGS"
            
            if cfp.has_option(section, 'token'):
                self.args.token = cfp[section]['token']
            
            if cfp.has_option(section, 'interface'):
                self.args.interface = cfp[section]['interface']
            
            if cfp.has_option(section, 'repo_owner'):
                self.args.repo_owner = cfp[section]['repo_owner']
            
            if cfp.has_option(section, 'repo_name'):
                self.args.repo_name = cfp[section]['repo_name']
            
            if cfp.has_option(section, 'start_date'):
                try:
                    self.args.start_date = to_iso_format(cfp[section]['start_date'])
                except Exception:
                    raise GrasConfigError(msg="Please enter the `start_date` in ISO-8601 format!")
            
            if cfp.has_option(section, 'end_date'):
                try:
                    self.args.end_date = to_iso_format(cfp[section]['end_date'])
                except Exception:
                    raise GrasConfigError(msg="Please enter the `end_date` in ISO-8601 format!")
        
        if cfp.has_section("DATABASE-SETTINGS"):
            section = "DATABASE-SETTINGS"
            
            if cfp.has_option(section, 'dbms'):
                self.args.dbms = cfp[section]['dbms']
            
            if cfp.has_option(section, 'db_name'):
                self.args.db_name = cfp[section]['db_name']
            
            if cfp.has_option(section, 'db_username'):
                self.args.db_username = cfp[section]['db_username']
            
            if cfp.has_option(section, 'db_password'):
                try:
                    self.args.db_password = bool(cfp[section]['db_password'])
                except Exception:
                    raise GrasConfigError(msg="`db_password` should be either `True` or `False`!")
            
            if cfp.has_option(section, 'db_host'):
                self.args.db_host = cfp[section]['db_host']
            
            if cfp.has_option(section, 'db_port'):
                self.args.db_port = cfp[section]['db_port']
            
            if cfp.has_option(section, 'db_output'):
                self.args.db_output = cfp[section]['db_output']
            
            if cfp.has_option(section, 'db_log'):
                try:
                    self.args.db_log = cfp[section]['db_log']
                except Exception:
                    raise GrasConfigError(msg="`db_log` should be either `True` or `False`!")
        
        if cfp.has_section("OTHER"):
            section = "OTHER"
            
            if cfp.has_option(section, 'help'):
                self.args.help = cfp[section]['help']
            
            if cfp.has_option(section, 'animator'):
                self.args.animator = cfp[section]['animator']
            
            if cfp.has_option(section, 'operation'):
                self.args.operation = cfp[section]['operation']
            
            if cfp.has_option(section, 'clear_logs'):
                try:
                    self.args.clear_logs = cfp[section]['clear_logs']
                except Exception:
                    raise GrasConfigError(msg="`clear_logs` should be either `True` or `False`!")
            
            if cfp.has_option(section, 'output'):
                self.args.output = cfp[section]['output']


if __name__ == '__main__':
    logger = logging.getLogger("main")
    set_up_logging()
    
    logger.info("Starting GRAS...")
    
    GrasArgumentParser()
