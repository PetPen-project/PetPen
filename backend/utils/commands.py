import os
import json

from model import backend_model

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
