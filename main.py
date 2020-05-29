import argparse
import configparser
import json
import logging.config
import os
import shutil
import sys
import threading
import time
from datetime import datetime
from queue import Queue

import numpy as np
import pandas as pd
from tabulate import tabulate

from gras.errors import GrasArgumentParserError, GrasConfigError
from gras.git.git_miner import GitMiner
from gras.github.github_miner import GithubMiner
from gras.github.github_repo_stats import RepoStatistics
from gras.identity_merging.identity_merging import IdentityMerging
from gras.utils import (
    ANIMATORS, DEFAULT_END_DATE, DEFAULT_START_DATE, ELAPSED_TIME_ON_FUNCTIONS, STAGE_WISE_TIME, set_up_token_queue,
    to_iso_format,
    )

LOGFILE = os.getcwd() + '/logs/{0}.{1}.log'.format(
    'gras', datetime.now().strftime('%Y-%m-%d %H-%M-%S %Z'))

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


def create_log_folder(path):
    """
    Creates the log folder
    
    Args:
        path: The log folder path
    """
    if not os.path.exists(path):
        os.makedirs(path)


def set_up_logging():
    logging.basicConfig(level=logging.ERROR)
    create_log_folder(os.getcwd() + '/logs')
    logging.config.dictConfig(DEFAULT_LOGGING)


def get_repo_stats(args, repo_list=None):
    if repo_list:
        # repo_list: (owner, name, start_date, end_date)
        pass
    else:
        repo_stats = RepoStatistics(
            token=args.tokens[0],
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
            add_help=True,
            #TODO: complete usage and add custom help argument
            usage='''main.py [-v, --version] [-v, --version]......
                <interface> [<args>]
                  '''
            )

        self.gras_command_groups = argparse.ArgumentParser(add_help=False)
        self.gras_setting_groups = argparse.ArgumentParser(add_help=False)
        self.database_groups = argparse.ArgumentParser(add_help=False)
        
        self._init_groups()
        self._add_gras_commands()
        self._add_gras_settings()
        self._add_database_settings()
        self._add_other_arguments()
        self._init_subparsers()
        self._init_git_parser()
        
        try:
            self.args = self.parse_args()
        except Exception as e:
            logger.error(e)
            sys.exit(1)

        if self.args.tokens is not None:
            set_up_token_queue(self.args.tokens)

        if self.args.db_password:
            self.args.db_password = input('Enter Password: ')

        if self.args.config:
            self._read_config()

        self._set_arg_groups()
        self._validate()
        self._execute()

    @property
    def action_groups(self):
        return self._action_groups

    def _init_subparsers(self):
        self.subparsers = self.add_subparsers(title='interfaces', dest="interface",
                                              parser_class=argparse.ArgumentParser)
        self.github_parser = self.subparsers.add_parser("github", parents=[self.gras_setting_groups,
                                                                           self.gras_command_groups,
                                                                           self.database_groups])
        self.gitlab_parser = self.subparsers.add_parser("gitlab", parents=[self.gras_setting_groups,
                                                                           self.gras_command_groups,
                                                                           self.database_groups])
        self.git_parser = self.subparsers.add_parser("git", parents=[self.gras_command_groups, self.database_groups])

    def _init_github_parser(self):
        # TODO: maybe add specific arguments
        pass

    def _init_gitlab_parser(self):
        # TODO: maybe add specific arguments
        pass

    def _init_git_parser(self):
        self.git_parser.add_argument('-gp', '--gitpath', help="Path to the .git file")

    def _init_groups(self):
        self.gras_commands = self.gras_command_groups.add_argument_group('GRAS-COMMANDS')
        self.gras_settings = self.gras_setting_groups.add_argument_group('GRAS-SETTINGS')
        self.database_settings = self.database_groups.add_argument_group('DATABASE-SETTINGS')
        self.other = self.add_argument_group('OTHER')

    def _add_gras_commands(self):

        self.gras_commands.add_argument('-s', '--stats', help="View the stats of the repository", default=False,
                                        type=bool, const=True, nargs='?')
        self.gras_commands.add_argument('-g', '--generate', help="Generate a config file template", default=False,
                                        type=bool, const=True, nargs='?')
        self.gras_commands.add_argument('-m', '--mine', help="Mine the repository", default=False, type=bool,
                                        const=True, nargs='?')
        self.gras_commands.add_argument('-id', '--identity-merging', help="Merge the identities of the contributors",
                                        default=False, type=bool, const=True, nargs='?')
        self.gras_commands.add_argument('-B', '--basic', help="Mining Stage 1-A: Basic", const=True, type=bool,
                                        nargs='?', default=False)
        self.gras_commands.add_argument('-BE', '--basic-extra', help="Mining Stage 1-B: Basic Extra", const=True,
                                        type=bool, nargs='?', default=False)
        self.gras_commands.add_argument('-IT', '--issue-tracker', help="Mining Stage 2: Issue Tracker", const=True,
                                        type=bool, nargs='?', default=False)
        self.gras_commands.add_argument('-CD', '--commit', help="Mining Stage 3: Commit Data", const=True, type=bool,
                                        nargs='?', default=False)
        self.gras_commands.add_argument('-PT', '--pull-tracker', help="Mining Stage 4: Pull Request Tracker",
                                        const=True, type=bool, nargs='?', default=False)
        self.gras_commands.add_argument('-CS', '--chunk-size', help="Time Period Chunk Size (in Days)", type=int,
                                        default=20)
        self.gras_commands.add_argument('-f', '--full', help="Mine the complete repository", const=True, nargs='?',
                                        type=bool)
        self.gras_settings.add_argument('--path', help="Path to the directory to mine")

    def _add_gras_settings(self):
        self.gras_settings.add_argument('-t', '--tokens', help="List of Personal API Access Tokens for parsing",
                                        nargs='+')
        self.gras_settings.add_argument('-yk', '--yandex-key', help="Yandex Translator API Key ("
                                                                    "https://translate.yandex.com/developers/keys)")
        self.gras_settings.add_argument('-i', '--interface', help="Interface of choice", default='github',
                                        choices=['github', 'git', 'identity-merging'], required=False)
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
                                            help="The database server db_port that allows communication to your "
                                                 "database", default=3306, type=int)
        self.database_settings.add_argument('-dbo', '--db-output',
                                            help="The path to the .db file in case of sqlite dbms")
        self.database_settings.add_argument('-dbl', '--db-log', help="DB-log flag to log the generated SQL produced",
                                            default=False, type=bool, nargs='?', required=False, const=True)

    def _add_other_arguments(self):
        self.other.add_argument('-a', '--animator', help="Loading animator", default='bar',
                                choices=list(ANIMATORS.keys()), required=False)
        self.other.add_argument('-OP', '--operation',
                                help="Choose the operation to perform for retrieving the stats.: 1. CREATE, 2. UPDATE, "
                                     "3. APPEND", choices=['1', '2', '3'], default='1')
        self.other.add_argument('-CL', '--clear-logs', help="Clear the logs directory", const=True, type=bool,
                                nargs='?', default=False)
        self.other.add_argument('-o', '--output', help="The output path where the config file is to be generated",
                                default=f"{os.getcwd()}/gras.ini")
        self.other.add_argument('-v', '--version', help="The version of GRAS installed", const=True, type=bool,
                                nargs='?', default=False)

    def _validate(self):
        args = self.args

        if (args.stats and args.generate) or (args.stats and args.mine) or (args.generate and args.mine):
            raise GrasArgumentParserError(msg="Only one GRAS command should be passed.")

        if args.generate:
            if not args.output:
                logger.warning(f"Output path not provided, using default: {os.getcwd()}/gras.ini")

        if args.stats or args.mine:
            if not args.tokens:
                raise GrasArgumentParserError(msg="Please provide at least 1 token!")

            if not args.start_date and not args.full:
                logger.warning(f"Start date not provided, using default start date: {DEFAULT_START_DATE}.")

            if not args.end_date and not args.full:
                logger.warning(f"End data not provided, using default end date: {DEFAULT_END_DATE}.")

            if not args.repo_name or not args.repo_owner:
                if not args.config:
                    raise GrasArgumentParserError(msg="Either Repo-name and Repo-owner or GrasConfig file should "
                                                      "be provided!")

        if args.mine:
            if args.dbms == "sqlite" and not args.db_output:
                logger.warning(f"SQLite database output file path not provided, using path: {os.getcwd()}/gras.db")

            if args.dbms != "sqlite":
                if not args.db_username or not args.db_password:
                    raise GrasArgumentParserError(msg="Please enter valid database credentials.")

            if args.db_username and args.db_password and not args.db_name:
                logger.warning(
                    "Database name not provided! GRAS will create the database with name `gras` if not exists.")

            if not args.basic and not args.basic_extra and not args.issue_tracker and not args.commit and \
                    not args.pull_tracker:
                logger.warning("Stage name not specified, using `basic` by default.")
                args.basic = True

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
                    logger.error('Failed to delete %s. Reason: %s' % (file_path, e))

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

            while t.is_alive():
                animated_loading(f"{now} - main - INFO - Fetching `{self.args.repo_name}` statistics", ANIMATORS[
                    self.args.animator])

            t.join()
            result = queue.get()

            print("\n\n", "=" * 100, "\n", json.dumps(result, indent=4, sort_keys=True), "\n", "=" * 100)

        if self.args.identity_merging:
            im = IdentityMerging(args=self.args)
            im.process()

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
                    key_lst = cfp[section][key].split('/')
                    value = cfp[section][key].split(',')

                    if value[0] is None:
                        value[0] = DEFAULT_START_DATE

                    if value[1] is None:
                        value[1] = DEFAULT_END_DATE

                    repos.append((key_lst[0], key_lst[1], value[0], value[1]))
            except Exception:
                raise GrasConfigError(msg="Please check REPOSITORY-LIST section.")

            self.repo_list = repos

        if cfp.has_section("GRAS-SETTINGS"):
            section = "GRAS-SETTINGS"

            if cfp.has_option(section, 'tokens'):
                self.args.tokens = cfp[section]['tokens']

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


def print_func_timings(dic, name, col_name):
    sys.stdout.write("\n")

    function_time = []
    for f, te in dic.items():
        function_time.append([f, te])

    total_time = sum([float(_) for _ in np.array(function_time)[:, 1].tolist()])

    function_time.append(["Total", total_time])

    df = pd.DataFrame(data=np.array(function_time), columns=[col_name, "Time Taken"])
    df.style.set_caption(name)

    sys.stdout.write(tabulate([list(row) for row in df.values], headers=list(df.columns), tablefmt='fancy_grid'))

    sys.stdout.write("\n")


def main():
    GrasArgumentParser()

    if ELAPSED_TIME_ON_FUNCTIONS:
        print_func_timings(ELAPSED_TIME_ON_FUNCTIONS, name="Function Timings", col_name="Function")

    if STAGE_WISE_TIME:
        print_func_timings(STAGE_WISE_TIME, name="Stage Timings", col_name="Stage")


if __name__ == '__main__':
    logger = logging.getLogger("main")
    set_up_logging()

    logger.info("Starting GRAS...")

    main()
    sys.exit(1)
