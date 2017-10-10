import os
import re
import json

from datetime import datetime
from model import backend_model
from utils import save_history
from utils import Batch_History, Model_state

def build_model(args):
    model_dir = os.path.dirname(args.model)
    model_path = args.model

    data_path = args.dataset

    model = backend_model(model_path, data_path)

    weights_path = os.path.join(model_dir,'weights.h5')

    if args.w:
        record_files = [f for f in os.listdir(model_dir) if re.match(r'\d{6}_\d{6}',f)]
        if not record_files:
            print('No weight file found. Skip weight loading step.')
        else:
            weight_file = os.path.join(max(record_files),'weights.h5')
        if os.path.exists(weight_file):
            model.load_weights(weight_file)

    return model, model_dir

def train_func(args):
    model, model_dir = build_model(args)

    # Callback_1
    history_callback = Batch_History()
    str_start_time = datetime.now().strftime('%y%m%d_%H%M%S')
    model_result_path = os.path.join(model_dir, str_start_time)
    os.mkdir(model_result_path)
    trainlog_dir = os.path.join(model_result_path,'logs')
    os.mkdir(trainlog_dir)

    # Callback_2
    state_file = os.path.join('.','state.json')
    state_callback = Model_state(state_file,model.config)
    history = model.train(callbacks=[history_callback, state_callback])
    save_history(os.path.join(trainlog_dir,'train_log'), history, history_callback)
    model.save_weights(os.path.join(model_result_path,'weights.h5'))

def validate_func(args):
    model, model_dir = build_model(args)
    loss = model.evaluate()
    print(loss)

def predict_func(args):
    testdata = None # feed some test data
    model, model_dir = build_model(args)
    loss = model.predict(testdata)
    print(loss)


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
