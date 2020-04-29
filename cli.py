import argparse
import sys
from pprint import pprint

import requests

from components.query_engine.structs.label_struct import LabelStruct
from components.query_engine.structs.language_struct import LanguageStruct
from components.query_engine.structs.milestone_struct import MilestoneStruct
from components.query_engine.structs.repository_struct import RepositoryStruct
from components.query_engine.structs.watcher_struct import WatcherStruct
from local_settings import AUTH_KEY

structs = ['language', 'lang', 'label', 'lab', 'milestone', 'miles', 'repo-data', 'watchers', 'watc']


# ----INITIALIZER----------TODO:AUTHENTICATE AUTH KEY/USERNAME&PASS,UPDATE USAGE AND HELP COMMANDS

def init(args):
    return args.authkey


parser = argparse.ArgumentParser(description='GITSTRUCT \n gather data from software repositories')
subparsers = parser.add_subparsers(help='command')
i_parser = subparsers.add_parser('init', help='initialize GitStruct')
i_parser.add_argument("-a", "--authkey", type=str, help="enter your github authentication key")
i_parser.add_argument("-u", "--username", type=str, help="enter your github username")
i_parser.add_argument("-p", "--password", type=str, help="enter your github password")
i_parser.set_defaults(func=init)


# ----STRUCT GENERATION--------
def generate(args):
    params = (AUTH_KEY, *args.repo.split('/'))
    if '/' not in args.repo:
        parser.error('repo entry must be in the format (owner/name)')
    elif not requests.get("https://api.github.com/repos/{}".format(args.repo)).ok:
        parser.error("repo does not exist")
    else:
        if args.struct == "all":
            complete = [LanguageStruct(*params).iterator(),
                        LabelStruct(*params).iterator(), MilestoneStruct(*params).iterator()]
            return complete
        elif args.struct in ("language", "lang"):
            lang_list = LanguageStruct(*params).iterator()
            return lang_list
        elif args.struct in ("label", "lab"):
            label_list = LabelStruct(*params).iterator()
            return label_list
        elif args.struct in ("milestone", "miles"):
            ms_list = MilestoneStruct(*params).iterator()
            return ms_list
        elif args.struct in "repo-meta":
            repo_meta_list = RepositoryStruct(AUTH_KEY, "https://github.com/{}".format(args.repo)).iterator()
            return repo_meta_list
        elif args.struct in ("watchers", "watc"):
            watcher_list = WatcherStruct(*params).iterator()
            return watcher_list


gen_parser = subparsers.add_parser('gen', help='parse the given repository')
gen_parser.add_argument("-r", "--repo", type=str, metavar='sympy/sympy', help="enter owner and name of the repo in \
            the format owner/name")
# parser.add_argument("-o","owner",type=str,help="owner of the repo ")
gen_parser.add_argument("-w", "--struct", type=str, default="all", choices=structs,
                        metavar='label', help="what you wish to parse")
gen_parser.add_argument("-l", "--limit", type=int, default="100", help="what you wish to parse")
gen_parser.set_defaults(func=generate)

config = parser.parse_args()

if __name__ == '__main__':
    sys.stdout.write(str(pprint(config.func(config))))

    # repo_check(args.repo)
    # list = generate(args.repo)
    # sys.stdout.write(str(pprint(list)))
