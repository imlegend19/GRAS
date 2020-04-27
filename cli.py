from label_struct import LabelStruct
from language_struct import LanguageStruct
from pprint import pprint
import argparse,sys
from local_settings import AUTH_KEY


parser = argparse.ArgumentParser(description='GITSTRUCT \n gather data from software repositories')
parser.add_argument("name", type=str,help="name of the repo you wish to parse")
parser.add_argument("owner",type=str,help="owner of the repo")
parser.add_argument("-w","--struct", type=str,default="all", help="what you wish to parse")
args = parser.parse_args()

def generate(struct,name,owner):
    if struct == "all":
        complete = [LanguageStruct(github_token=AUTH_KEY,name=name,owner=owner).iterator(), 
        LabelStruct(github_token=AUTH_KEY,name=name,owner=owner).iterator()]
        return complete
    elif struct in ("language", "lang"):
        lang_list = LanguageStruct(github_token=AUTH_KEY,name=name,owner=owner).iterator()
        return lang_list
    elif struct in ("label", "lab"):
        label_list = LabelStruct(github_token=AUTH_KEY,name=name,owner=owner).iterator()
        return label_list

if __name__ == '__main__':
    list = generate(args.struct,args.name,args.owner)
    sys.stdout.write(str(pprint(list)))
