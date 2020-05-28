import  argparse

parser = argparse.ArgumentParser()

# Usual arguments which are applicable for the whole script / top-level args
parser.add_argument('--verbose', help='Common top-level parameter',
                    action='store_true', required=False)

# Same subparsers as usual
subparsers = parser.add_subparsers(help='Desired action to perform', dest='action')

# Usual subparsers not using common options
parser_other = subparsers.add_parser("extra-action", help='Do something without db')

# Create parent subparser. Note `add_help=False` and creation via `argparse.`
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('-p', help='add db parameter', required=True)
c = parent_parser.add_argument_group('GRAS-COMMANDS')
c.add_argument('-w')

# Subparsers based on parent

parser_create = subparsers.add_parser("create", parents=[parent_parser],
                                      help='Create something')
# Add some arguments exclusively for parser_create

parser_update = subparsers.add_parser("update", parents=[parent_parser],
                                      help='Update something')

print(parser.parse_args())