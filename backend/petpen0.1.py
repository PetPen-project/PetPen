import argparse
import time
from datetime import datetime
import sys,os,re
import pandas as pd

from model import get_model,backend_model
from utils import train_func, predict_func
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

#
# Ming: are model and validate really need?
#
subparser = subparsers.add_parser('train')
subparser.set_defaults(func=train_func)

subparser = subparsers.add_parser('predict')
subparser.set_defaults(func=predict_func)

args = parser.parse_args()
args.func(args)

'''
# Callback_1
b_history = Batch_History()
str_start_time = datetime.now().strftime('%y%m%d_%H%M%S')
model_result_path = os.path.join(model_dir, str_start_time)
os.mkdir(model_result_path)
trainlog_dir = os.path.join(model_result_path,'logs')
os.mkdir(trainlog_dir)

# Callback_2
state_file = os.path.join('.','state.json')
state = Model_state(state_file,model.config)

# Training
history = model.train(callbacks = [b_history,state])
save_history(os.path.join(trainlog_dir,'train_log'),history,b_history)
model.save_weights(os.path.join(model_result_path,'weights.h5'))

# Evaluate
model.evaluate()
save_history(os.path.join(trainlog_dir,'validate_log'),history,b_history)
'''
