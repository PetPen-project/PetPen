import os
import re
import json

from model import backend_model

def build_model_command(args):
    model_dir = args.model
    model_file = 'result.json'
    model_path = os.path.join(model_dir,model_file)
    model = backend_model(model_path)

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

def training_command(args):
    # model, model_dir = build_model(args)
    # model.train
    pass

    


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
