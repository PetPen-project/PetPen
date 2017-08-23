import argparse
import time
import sys,os,re
import pandas as pd

from model import get_model,backend_model
from data_provider import Demo1,Mnist
from utils import build_model_command
from utils import get_command,Batch_History,Model_state,load_dataset
from utils import save_history
from keras.callbacks import TensorBoard

parser = argparse.ArgumentParser(prog='petpen')
subparsers = parser.add_subparsers()
subparser = subparsers.add_parser('model')
subparser.add_argument('-n', '--name', default='result', help='specify the model name.')
subparser.add_argument('-m', '--model', required=True, help='set model folder')
subparser.add_argument('-d', '--dataset', required=True, help='set dataset folder')
subparser.set_defaults(func=build_model_command)
parser.add_argument('-w', default='False', help='set -w True to load weight')

args = parser.parse_args()
model,model_dir = args.func(args)

# (x_train,y_train),(x_test,y_test) = data.load_dataset(args.d,model.features)

if args.name == 'demo1':
    data = Demo1()
elif args.name == 'mnist' or 'mnist_cnn':
    data = Mnist()
(x_train,y_train),(x_test,y_test) = data.load_data()


b_history = Batch_History()
trainlog_path = os.path.join(model_dir,'logs')
if not os.path.exists(trainlog_path):
    os.mkdir(trainlog_path)

state_file = os.path.join('/home/plash/petpen/','state.json')
state = Model_state(state_file,model.config)

history = model.train(x_train,y_train,callbacks = [b_history,state])
trainlog_name = 'train_log'#+'_'+str(int(time.time()))
pd.DataFrame(history.history).to_csv(os.path.join(trainlog_path,trainlog_name),index=False)
pd.DataFrame(b_history.history).to_csv(os.path.join(trainlog_path,trainlog_name+'full'),index=False)

model.save_weights('weights.h5')
print(model.model.layers[1].weights)

time.sleep(1)
model.evaluate(x_test,y_test)

trainlog_name = 'test_log'#+'_'+str(int(time.time()))
pd.DataFrame(history.history).to_csv(os.path.join(trainlog_path,trainlog_name),index=False)
pd.DataFrame(b_history.history).to_csv(os.path.join(trainlog_path,trainlog_name+'full'),index=False)

# y_test = model.predict(x_test)
# pd.DataFrame(y_test).to_csv(os.path.join(trainlog_path,'result.csv'),index=False)


# while True:
    # cmd = get_command()
    # print(cmd)
    # if cmd == 'exit':
        # break
    # if cmd not in ['train','predict']:
        # continue
    # if cmd == 'train':
        # history = model.train(x_train,y_train,callbacks = [b_history,state])
        # trainlog_name = 'train_log'#+'_'+str(int(time.time()))
        # pd.DataFrame(history.history).to_csv(os.path.join(trainlog_path,trainlog_name),index=False)
        # pd.DataFrame(b_history.history).to_csv(os.path.join(trainlog_path,trainlog_name+'full'),index=False)

    # if cmd == 'predict':
        # # model.evaluate(x_test,y_test)
        # y_test = model.predict(x_test)
        # pd.DataFrame(y_test).to_csv(os.path.join(trainlog_path,'result.csv'),index=False)

# if __name__ = '__main__':

