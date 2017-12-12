import argparse
from utils import train_func, validate_func, predict_func

parser = argparse.ArgumentParser(prog='petpen')
subparsers = parser.add_subparsers()

parser.add_argument('-m', '--model', required=True, help='set model folder')
parser.add_argument('-trainx', '--trainx', required=False, default=None, help='train input')
parser.add_argument('-trainy', '--trainy', required=False, default=None, help='train label')
parser.add_argument('-testx', '--testx', required=False, default=None, help='test input')
parser.add_argument('-testy', '--testy', required=False, default=None, help='test output')
parser.add_argument('-w', '--weight', required=False, default=None, help='set -w to load weight')

subparser = subparsers.add_parser('train')
subparser.set_defaults(func=train_func)

subparser = subparsers.add_parser('validate')
subparser.set_defaults(func=validate_func)

subparser = subparsers.add_parser('predict')
subparser.set_defaults(func=predict_func)


args = parser.parse_args()
args.func(args)

