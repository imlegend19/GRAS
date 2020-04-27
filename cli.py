from label_struct import LabelStruct
from language_struct import LanguageStruct
from milestone_struct import MilestoneStruct
from repository_struct import RepositoryStruct
from watcher_struct import WatcherStruct

from pprint import pprint
import argparse,sys
from local_settings import AUTH_KEY


parser = argparse.ArgumentParser(description='GITSTRUCT \n gather data from software repositories')
# parser.add_argument("action", type=str,default="generate",help="actions: gen/generate \n")
parser.add_argument("name",type=str,help="name of the repo ")
parser.add_argument("owner",type=str,help="owner of the repo ")
parser.add_argument("-w","--struct", type=str,default="all", help="what you wish to parse")
parser.add_argument("-l","--limit", type=int,default="100", help="what you wish to parse")
args = parser.parse_args()


def generate(name,owner):
    params = (AUTH_KEY,name,owner)

    if args.struct == "all":
        complete = [LanguageStruct(*params).iterator(), 
        LabelStruct(*params).iterator(), MilestoneStruct(*params).iterator() ]
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
    elif args.struct in ("repo-data"):
        repodata_list = RepositoryStruct(AUTH_KEY,"https://github.com/{}/{}".format(owner,name)).iterator()
        return repodata_list
    elif args.struct in ("watchers", "watc"):
        watcher_list = WatcherStruct(*params).iterator()
        return watcher_list   
    # elif args.struct in ("issue","iss"):
    #     issue_list = IssueStruct(*params).iterator(args.limit)

    # TODO: @ayankashyap Raise an exception for entering invalid parameter. 


if __name__ == '__main__':
    list = generate(args.name,args.owner)
    sys.stdout.write(str(pprint(list)))
