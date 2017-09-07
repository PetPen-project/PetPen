import argparse
import time
from datetime import datetime
import sys,os,re
import pandas as pd

from model import get_model,backend_model
from utils import build_model_command
from utils import Batch_History,Model_state,load_dataset
from utils import save_history
import utils
# from keras.callbacks import TensorBoard

parser = argparse.ArgumentParser(prog='petpen')
subparsers = parser.add_subparsers()
parser.add_argument('-n', '--name', default='result', help='specify the model name.')
parser.add_argument('-m', '--model', required=True, help='set model folder')
parser.add_argument('-d', '--dataset', required=True, help='set dataset folder')
parser.add_argument('-w', dest='w',action='store_true', help='set -w to load weight')
parser.set_defaults(w=False)

subparser = subparsers.add_parser('model')
subparser.set_defaults(func=build_model_command)

subparser = subparsers.add_parser('train')
subparser.set_defaults(func=build_model_command)

subparser = subparsers.add_parser('validate')
subparser.set_defaults(func=build_model_command)

subparser = subparsers.add_parser('predict')
subparser.set_defaults(func=build_model_command)

args = parser.parse_args()
model,model_dir = args.func(args)

b_history = Batch_History()
str_start_time = datetime.now().strftime('%y%m%d_%H%M%S')
model_result_path = os.path.join(model_dir, str_start_time)
os.mkdir(model_result_path)

trainlog_dir = os.path.join(model_result_path,'logs')
os.mkdir(trainlog_dir)

state_file = os.path.join('/home/plash/petpen/','state.json')
state = Model_state(state_file,model.config)

if args.w:
    record_files = [f for f in os.listdir(model_dir) if re.match(r'\d{6}_\d{6}',f)]
    if not record_files:
        print('no saved weight found.')
    else:
        weight_file = os.path.join(max(record_files),'weights.h5')
    if os.path.exists(weight_file):
        model.load_weights(weight_file)

history = model.train(callbacks = [b_history,state])
save_history(os.path.join(trainlog_dir,'train_log'),history,b_history)
model.save_weights(os.path.join(model_result_path,'weights.h5'))

time.sleep(1)
model.evaluate()
save_history(os.path.join(trainlog_dir,'validate_log'),history,b_history)

