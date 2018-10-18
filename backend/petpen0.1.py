import argparse, os, sys, json
from utils import train_func, validate_func, predict_func
from utils import change_status
from datetime import datetime
import traceback


parser = argparse.ArgumentParser(prog='petpen')
subparsers = parser.add_subparsers()

parser.add_argument('-m', '--model', required=True, help='set model folder')
parser.add_argument('-trainx', '--trainx', required=False, default=None, help='train input')
parser.add_argument('-trainy', '--trainy', required=False, default=None, help='train label')
parser.add_argument('-testx', '--testx', required=False, default=None, help='test input')
parser.add_argument('-testy', '--testy', required=False, default=None, help='test output')
parser.add_argument('-w', '--weight', required=False, default=None, help='set -w to load weight')
parser.add_argument('-t', '--time', required=False, default=None, help='set -t to indicate backend start time')
parser.add_argument('-id', '--id', required=False, default=None, help='project id')
parser.add_argument('-header', '--header', required=False, default=False, help='whether to parse the csv header')

subparser = subparsers.add_parser('train')
subparser.set_defaults(func=train_func)

subparser = subparsers.add_parser('validate')
subparser.set_defaults(func=validate_func)

subparser = subparsers.add_parser('predict')
subparser.set_defaults(func=predict_func)


args = parser.parse_args()

model_dir = args.model

if 'train' in args.func.__name__:
    log_dir_name = args.time if args.time else datetime.now().strftime('%y%m%d_%H%M%S')
else:
    log_dir_name = 'result'

model_result_path = os.path.join(model_dir, log_dir_name)

if not os.path.exists(model_result_path):
    os.mkdir(model_result_path)

log_dir = os.path.join(model_result_path, 'logs')
os.mkdir(log_dir)

error_log_file = os.path.join(log_dir, 'error_log')

id = args.id

try:
    if 'train' in args.func.__name__:
        args.func(args, log_dir)
    else:
        args.func(args, model_result_path)
    
    change_status('finish', id)

except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    with open(error_log_file, 'w') as error_log:
        for line in lines:
            error_log.write(line)
    with open(os.path.join(model_dir,'state.json'),'w') as state_file:
        info = {
            'status':'error',
            'error_log_file':error_log_file
            }
        json.dump(info,state_file)
    
    change_status('error', id)


