import time
import json
import os
from keras.callbacks import Callback

from model import backend_model

def get_command(prompt="waiting for command(train/predict): "):
    import termios, sys
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ECHO          # lflags
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new)
        cmd = input(prompt)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return cmd

def build_model_command(args):
    model_dir = args.model
    model_file = 'result.json'
    model_path = os.path.join(model_dir,model_file)
    model = backend_model(model_path)

    weights_path = os.path.join(model_dir,'weights.h5')
    if args.w == 'True' and os.path.isfile(weights_path):
        model.load_weights(weights_path)
    elif args.w == 'True':
        print('No weight file found. Skip weight loading step.')

    return model, model_dir

def save_history(file_path,history,full_history=None):
    pd.DataFrame(history.history).to_csv(file_path,index=False)
    pd.DataFrame(full_history.history).to_csv(file_path+'full',index=False)

class Model_state(Callback):
    """record model execution state.
    """

    def __init__(self,state_file,config=None):
        self.config = config
        self.info = {}
        self.info['status'] = 'waiting command'
        self.info['time'] = time.asctime()
        self.info['progress'] = []
        self.info['epoch'] = []
        self.info['loss'] = {'type':self.config['loss'], 'value':None}
        self.file_path = state_file
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_train_begin(self, logs=None):
        self.info['status'] = 'start training model'
        self.info['time'] = time.asctime()
        self.info['epoch'] = [0,self.params['epochs']]
        self.info['loss']['type'] = self.config['loss']
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_train_end(self, logs=None):
        self.info['status'] = 'finish training'
        self.info['time'] = time.asctime()
        # self.info['progress'] = []
        # self.info['epoch'] = []
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_epoch_begin(self, epoch, logs=None):
        self.info['epoch'][0] = epoch+1
        self.info['progress'] =[0,self.params['samples']]
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_batch_begin(self, batch, logs=None):
        self.info['progress'][0] = min((batch+1)*self.params['batch_size'], self.params['samples'])
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_batch_end(self, batch, logs=None):
        self.info['loss']['value'] = float(logs.get('loss'))
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_epoch_end(self, epoch, logs=None):
        self.info['loss']['value'] = float(logs.get('loss'))
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_test_begin(self, logs=None):
        self.info['status'] = 'start testing'
        self.info['time'] = time.asctime()
        self.info['progress'] = [0,self.params['samples']]
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    def on_test_end(self, test_loss):
        self.info['status'] = 'job done'
        self.info['time'] = time.asctime()
        if len(test_loss)>1:
            test_loss = sum(test_loss)/len(test_loss)
        else:
            test_loss = test_loss[0]
        self.info['loss']['value'] = float(test_loss)
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)


class Batch_History(Callback):
    """Callback that records events into a `History` object.
    This callback is used to save computed metrics on the
    end of each batch. The `History` object
    gets returned by the `fit` method of models.
    """

    def on_train_begin(self, logs=None):
        self.batch = []
        self.history = {}

    def on_batch_end(self, batch, logs=None):
        logs = logs or {}
        self.batch.append(batch)
        for k, v in logs.items():
            self.history.setdefault(k, []).append(v)

def StateLogger(Callback):
    """Callback that saves the running progress into a json file.
    """
    
    def __init__(self):
        pass
    def on_train_begin(self, logs=None):
        self.batch = []

def load_dataset(file_path,features,target,separate_testing=True,testing_percent=0.3,shuffle_dataset=False,**kwargs):
    import pandas as pd
    dataset = pd.read_csv(file_path)
    if shuffle_dataset:
        dataset = dataset.sample(frac=1).reset_index(drop=True)
    x = dataset[features]
    y = dataset[target]
    if separate_testing:
        train_x = x.iloc[:x.shape[0]*(1-testing_percent)]
        test_x = x.iloc[x.shape[0]*(1-testing_percent):]
        train_y = y.iloc[:y.shape[0]*(1-testing_percent)]
        test_y = y.iloc[y.shape[0]*(1-testing_percent):]
        return (train_x,train_y), (test_x,test_y)
    return x, y


