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
            'level'    : 'INFO',
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


def get_repo_stats(args):
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


def start():
    logger = logging.getLogger("main")
    set_up_logging()
    
    logger.info("Starting GRAS...")
    
    parser = argparse.ArgumentParser(description='GRAS - GIT REPOSITORIES ARCHIVING SERVICE', add_help=False)
    
    # ======
    # groups
    # ======
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    database = parser.add_argument_group('database setting')
    
    # ==================
    # required arguments
    # ==================
    # TODO: remove default after testing and add required=True
    required.add_argument('-RO', '--repo-owner', help="Owner of the repository", default="openshift")
    required.add_argument('-RN', '--repo-name', help="Name of the repository", default="openshift-ansible")
    required.add_argument('-t', '--token', help="Personal API Access Token for parsing", default=AUTH_KEY)
    
    # ==================
    # optional arguments
    # ==================
    optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
    optional.add_argument('-i', '--interface', help="Interface of choice", default='github', choices=['github'],
                          required=False)
    optional.add_argument('-SD', '--start-date',
                          help="Start Date for mining the data (in any ISO 8601 format, e.g., 'YYYY-MM-DD HH:mm:SS "
                               "+|-HH:MM')", default=DEFAULT_START_DATE, required=False)
    optional.add_argument('-ED', '--end-date',
                          help="End Date for mining the data (in any ISO 8601 format, e.g., 'YYYY-MM-DD HH:mm:SS "
                               "+|-HH:MM')", default=DEFAULT_END_DATE, required=False)
    optional.add_argument('-a', '--animator', help="Loading animator", default='bar', choices=list(ANIMATORS.keys()),
                          required=False)
    optional.add_argument('-s', '--stats', help="View the stats of the repo", default=False, type=bool, const=True,
                          nargs='?', required=False)
    
    # ================
    # database setting
    # ================
    database.add_argument('-dbms', help="DBMS to dump the data into", default='mysql', choices=["sqlite", "mysql",
                                                                                                "postgresql"])
    database.add_argument('-DB', '--db-name', help="Name of the database", default='gras')
    database.add_argument('-U', '--db-username', help="The user name that is used to connect and operate the selected "
                                                      "database")
    database.add_argument('-P', '--db-password', help="The password for the user name entered", const=True, nargs='?')
    database.add_argument('-H', '--db-host', help="The database server IP address or DNS name", default="localhost")
    database.add_argument('-p', '--db-port', help="The database server port that allows communication to your "
                                                  "database", default=3306, type=int)
    database.add_argument('-o', '--db-output', help="The path to the .db file in case of sqlite dbms")
    database.add_argument('-L', '--db-log', help="DB-log flag to log the generated SQL produced", default=False,
                          type=bool, nargs='?', required=False, const=True)
    
    args = parser.parse_args()
    
    if args.db_password:
        args.db_password = getpass.getpass('Enter Password: ')
    
    if args.stats:
        queue = Queue()
        t = threading.Thread(name='process', target=lambda q, arg1: q.put(get_repo_stats(arg1)), args=(queue, args))
        t.daemon = True
        t.start()
        
        now = datetime.now().strftime('%d/%d/%Y %H:%M:%S')
        
        while t.isAlive():
            animated_loading(f"{now} - main - INFO - Fetching `{args.repo_name}` statistics", ANIMATORS[args.animator])
        
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