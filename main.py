import argparse
import logging.config
import os
import sys
import threading
import time
from datetime import datetime
from queue import Queue
import getpass

from components.github_miner import GithubMiner
from components.query_engine.github_repo_stats import RepoStatistics
from components.utils import ANIMATORS, DEFAULT_END_DATE, DEFAULT_START_DATE, to_iso_format
from config import Config
from local_settings import AUTH_KEY

LOGFILE = os.getcwd() + '/logs/{0}.{1}.log'.format(
    os.path.basename(__file__),
    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

DEFAULT_LOGGING = {
    'version': 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%d/%m/%Y %H:%M:%S"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'stream': sys.stdout,
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'level': 'INFO',
            'filename': LOGFILE,
            'mode': 'w',
        },
    },
    'loggers': {
        "main": {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    }
}


def set_up_logging():
    logging.basicConfig(level=logging.ERROR)
    logging.config.dictConfig(DEFAULT_LOGGING)


def get_repo_stats(args):
    repo_stats = RepoStatistics(token=args.token,
                                name=args.repo_name,
                                owner=args.repo_owner,
                                start_date=to_iso_format(args.start_date),
                                end_date=to_iso_format(args.end_date))

    return repo_stats.repo_stats()


def animated_loading(msg, animator):
    chars = animator

    for char in chars:
        sys.stdout.write('\r' + f"{msg}: " + char + "\t")
        time.sleep(.2)
        sys.stdout.flush()


def start():
    logger = logging.getLogger("main")
    set_up_logging()
    cliConfig = Config()

    logger.info("Starting GRAS...")

    parser = argparse.ArgumentParser(
        description='GRAS - GIT REPOSITORIES ARCHIVING SERVICE',
        add_help=False)

    # ======
    # groups
    # ======
    gras_commands = parser.add_argument_group('GRAS-COMMANDS')
    database_settings = parser.add_argument_group('DATABASE-SETTINGS')
    miner_settings = parser.add_argument_group('MINER-SETTINGS')
    other = parser.add_argument_group('OTHER')

    # ==================
    # gras commands
    # ==================
    # TODO: remove default after testing and add required=True

    gras_commands.add_argument('-s',
                               '--stats',
                               help="View the stats of the repo",
                               default=False,
                               type=bool,
                               const=True,
                               nargs='?',
                               required=False)

    gras_commands.add_argument('-g',
                               '--generate',
                               help="generate a config file",
                               default=False,
                               type=bool,
                               const=True,
                               nargs='?',
                               required=False)
    gras_commands.add_argument('-m',  # ??
                               '--mine',
                               help="mine the repo",
                               default=False,
                               type=bool,
                               const=True,
                               nargs='?',
                               required=False)

    # ==================
    # miner setting
    # ==================
    miner_settings.add_argument('-RO',
                                '--repo-owner',
                                help="Owner of the repository",
                                default="apache")
    miner_settings.add_argument('-RN',
                                '--repo-name',
                                help="Name of the repository",
                                default="incubator-mxnet")
    miner_settings.add_argument('-t',
                                '--token',
                                help="Personal API Access Token for parsing",
                                default=AUTH_KEY)
    miner_settings.add_argument('-SD',
                                '--start-date',
                                help=
                                "Start Date for mining the data (in any ISO 8601 format, e.g., 'YYYY-MM-DD HH:mm:SS "
                                "+|-HH:MM')",
                                default=DEFAULT_START_DATE,
                                required=False)
    miner_settings.add_argument('-ED',
                                '--end-date',
                                help=
                                "End Date for mining the data (in any ISO 8601 format, e.g., 'YYYY-MM-DD HH:mm:SS "
                                "+|-HH:MM')",
                                default=DEFAULT_END_DATE,
                                required=False)
    miner_settings.add_argument('-i',
                                '--interface',
                                help="Interface of choice",
                                default='github',
                                choices=['github'],
                                required=False)

    # ================
    # database setting
    # ================
    database_settings.add_argument('-dbms',
                                   help="DBMS to dump the data into",
                                   default='mysql',
                                   choices=["sqlite", "mysql", "postgresql"])
    database_settings.add_argument('-DB',
                                   '--db-name',
                                   help="Name of the database",
                                   default='gras')
    database_settings.add_argument('-U',
                                   '--db-username',
                                   help="The user name that is used to connect and operate the selected "
                                        "database")
    database_settings.add_argument('-P',
                                   '--db-password',
                                   help="The password for the user name entered",
                                   const=True,
                                   nargs='?')
    database_settings.add_argument('-H',
                                   '--db-host',
                                   help="The database server IP address or DNS name",
                                   default="localhost")
    database_settings.add_argument('-p',
                                   '--db-port',
                                   help="The database server port that allows communication to your "
                                        "database",
                                   default=3306,
                                   type=int)
    database_settings.add_argument('-dbo',
                                   '--db-output',
                                   help="The path to the .db file in case of sqlite dbms")
    database_settings.add_argument('-L',
                                   '--db-log',
                                   help="DB-log flag to log the generated SQL produced",
                                   default=False,
                                   type=bool,
                                   nargs='?',
                                   required=False,
                                   const=True)

    # ================
    # other
    # ================
    other.add_argument("-h",
                       "--help",
                       action="help",
                       help="show this help message and exit")
    other.add_argument('-a',
                       '--animator',
                       help="Loading animator",
                       default='bar',
                       choices=list(ANIMATORS.keys()),
                       required=False)
    other.add_argument('-o',
                       '--output',
                       help="Path of the generated config file",
                       default=f"{os.getcwd()}config.cfg",
                       required=False)
    other.add_argument('-OP',
                       '--operation',
                       help="1: UPDATE, 2: APPEND, 3: CREATE ",
                       choices=['1', '2', '3'],
                       default='1',
                       required=False)

    args = parser.parse_args()
    args_dict = vars(args)
    arg_groups = {}
    for group in parser._action_groups:
        group_dict = {a.dest: getattr(args, a.dest, None) for a in group._group_actions}
        arg_groups[group.title] = argparse.Namespace(**group_dict)

    if args_dict['generate']:
        cliConfig._create_config('config', arg_groups)

    if args.db_password:
        args.db_password = getpass.getpass('Enter Password: ')

    if args.stats:
        queue = Queue()
        t = threading.Thread(
            name='process',
            target=lambda q, arg1: q.put(get_repo_stats(arg1)),
            args=(queue, args))
        t.daemon = True
        t.start()

        now = datetime.now().strftime('%d/%d/%Y %H:%M:%S')

        while t.isAlive():
            animated_loading(
                f"{now} - main - INFO - Fetching `{args.repo_name}` statistics",
                ANIMATORS[args.animator])

        t.join()
        result = queue.get()
        logger.debug(result)
    else:
        # TODO: Initialise the parsing and dump the data to the output location
        if args.interface == "github":
            gm = GithubMiner(args=args)
            gm.connect_to_db()
        else:
            pass


if __name__ == '__main__':
    start()
