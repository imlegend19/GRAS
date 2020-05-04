import argparse
import logging.config
import os
import sys
from datetime import datetime

from components.utils import DEFAULT_END_DATE, DEFAULT_START_DATE

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
    required.add_argument('-RO', '--repo-owner', help="Owner of the repository", required=True)
    required.add_argument('-RN', '--repo-name', help="Name of the repository", required=True)
    required.add_argument('-t', '--token', help="Personal API Access Token for parsing", required=True)
    
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
    
    optional.add_argument('-s', '--stats', help="View the stats of the repo", default=False, type=bool, const=True,
                          nargs='?', required=False)
    
    # ================
    # database setting
    # ================
    database.add_argument('-dbms', help="DBMS to dump the data into", default='sqlite3', choices=["sqlite3", "mysql",
                                                                                                  "postgresql"])
    database.add_argument('-DB', '--db-name', help="Name of the database", default='gras')
    database.add_argument('-U', '--db-username', help="The user name that is used to connect and operate the selected "
                                                      "database")
    database.add_argument('-P', '--db-password', help="The password for the user name entered")
    database.add_argument('-H', '--db-host', help="The database server IP address or DNS name", default="localhost")
    database.add_argument('-p', '--db-port', help="The database server port that allows communication to your database")
    
    args = parser.parse_args()
    
    if args.stats:
        # TODO: Display the stats of the repository
        pass
    else:
        # TODO: Initialise the parsing and dump the data to the output location
        pass


if __name__ == '__main__':
    start()