from gras.file_dependency.utils import lines_of_code_counter
from gras.file_dependency.py_files.node_parser import parse_dir
from pprint import pprint

# TODO: run this, maybe put parse_dir in this file, I am not sure how to structure this anymore
pprint(parse_dir('/home/viper/dev/GRAS/gras/file_dependency'))
