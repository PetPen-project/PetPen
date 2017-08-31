import time
import json
import os
from keras.callbacks import Callback
import pandas as pd

from model import backend_model

def save_history(file_path,history,full_history=None):
    pd.DataFrame(history.history).to_csv(file_path,index=False)
    if full_history:
        pd.DataFrame(full_history.history).to_csv(file_path+'full',index=False)

class Model_state(Callback):
    """record model execution state.
    """

    def __init__(self,state_file,config=None):
        self.config = config
        self.info = {}
        self.info['status'] = 'system idle'
        self.info['time'] = time.asctime()
        self.info['progress'] = []
        self.info['epoch'] = []
        self.info['loss'] = {'type':self.config['loss'], 'value':None}
        self.file_path = state_file
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)
    
    def save_status(self):
        with open(self.file_path,'w') as f:
            json.dump(self.info, f)

    def on_train_begin(self, logs=None):
        self.info['status'] = 'start training model'
        self.info['time'] = time.asctime()
        self.info['epoch'] = [0,self.params['epochs']]
        self.info['loss']['type'] = self.config['loss']
        self.save_status()
        
    def on_train_end(self, logs=None):
        self.info['status'] = 'finish training'
        self.info['time'] = time.asctime()
        self.save_status()

    def on_epoch_begin(self, epoch, logs=None):
        self.info['epoch'][0] = epoch+1
        self.info['progress'] =[0,self.params['samples']]
        self.save_status()

    def on_batch_begin(self, batch, logs=None):
        self.info['progress'][0] = min((batch+1)*self.params['batch_size'], self.params['samples'])
        self.save_status()

    def on_batch_end(self, batch, logs=None):
        self.info['loss']['value'] = float(logs.get('loss'))
        self.save_status()

    def on_epoch_end(self, epoch, logs=None):
        self.info['loss']['value'] = float(logs.get('loss'))
        self.save_status()
    def on_test_begin(self, logs=None):
        self.info['status'] = 'start testing'
        self.info['time'] = time.asctime()
        self.info['progress'] = [0,self.params['samples']]
        self.save_status()

    def on_test_end(self, test_loss):
        self.info['status'] = 'system idle'
        self.info['time'] = time.asctime()
        if len(test_loss)>1:
            test_loss = sum(test_loss)/len(test_loss)
        else:
            test_loss = test_loss[0]
        self.info['loss']['value'] = float(test_loss)
        self.save_status()


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


