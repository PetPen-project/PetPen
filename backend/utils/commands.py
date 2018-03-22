import os
import re
import json

from datetime import datetime
from model import backend_model, load_file
from utils import save_history
from utils import Batch_History, Model_state

from keras.models import load_model

def build_model(args):
    model_dir = args.model
    model_file = 'preprocessed/result.json'
    model_path = os.path.join(model_dir, model_file)

    trainx = args.trainx
    trainy = args.trainy
    testx = args.testx
    testy = args.testy

    weight_file = args.weight

    if weight_file:
        # record_files = [f for f in os.listdir(model_dir) if re.match(r'\d{6}_\d{6}',f)]
        # if not record_files:
            # print('No weight file found. Skip weight loading step.')
        # else:
            # weight_file = os.path.join(max(record_files), weight_file)
        # if os.path.exists(weight_file):
        model = load_model(weight_file)
    else:
        model = backend_model(model_path, trainx, trainy, testx, testy)

    model.summary()

    return model, model_dir, (trainx, trainy, testx, testy)

def train_func(args, log_dir):
    model, model_dir, (trainx, trainy, testx, testy) = build_model(args)

    # Callback_1
    history_callback = Batch_History()

    # Callback_2
    state_file = os.path.join(model_dir, 'state.json')
    #state_file = "/home/plash/petpen/state.json"
    state_callback = Model_state(state_file, model.config)
    history = model.train(callbacks=[history_callback, state_callback])
    save_history(os.path.join(log_dir,'train_log'), history, history_callback)
    model_result_path = os.path.dirname(log_dir)
    model.save(os.path.join(model_result_path,'weights.h5'))

def validate_func(args, log_dir):
    # Required: testx, testy, model_dir, weight
    pass


def predict_func(args, log_dir):
    # Required: testx, model_dir, weight

    test_data = load_file(args.testx)
    model = load_model(args.weight)
    result = model.predict(test_data)

    model_dir = args.model
    model_file = 'preprocessed/result.json'
    model_path = os.path.join(model_dir, model_file)
    with open(model_path) as f:
        model_parser = json.load(f)

    for key in model_parser['layers']:
        if 'output' in key:
            loss = model_parser['layers'][key]['params']['loss']

    if 'entropy' in loss:
        problem = 'classification'
    else:
        problem = 'regression'

    with open(os.path.join(log_dir, 'type'), 'w') as f:
        f.write(str(problem))

    with open(os.path.join(log_dir, 'result'), 'w') as f:
        for i in result:
            f.write(','.join(map(str, i)) + '\n')




