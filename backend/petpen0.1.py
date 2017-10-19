import argparse
from utils import train_func, validate_func, predict_func

parser = argparse.ArgumentParser(prog='petpen')
subparsers = parser.add_subparsers()

parser.add_argument('-m', '--model', required=True, help='set model folder')
parser.add_argument('-d', '--dataset', required=True, help='set dataset folder')
parser.add_argument('-w', dest='w',action='store_true', help='set -w to load weight')
parser.set_defaults(w=False)

subparser = subparsers.add_parser('train')
subparser.set_defaults(func=train_func)

subparser = subparsers.add_parser('validate')
subparser.set_defaults(func=validate_func)

subparser = subparsers.add_parser('predict')
subparser.set_defaults(func=predict_func)


args = parser.parse_args()
args.func(args)

