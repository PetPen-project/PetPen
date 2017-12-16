import os
import re
import json

from datetime import datetime
from model import backend_model
from utils import save_history
from utils import Batch_History, Model_state

def build_model(args):
    model_dir = args.model
    model_file = 'preprocessed/result.json'
    model_path = os.path.join(model_dir, model_file)

    trainx = args.trainx
    trainy = args.trainy
    testx = args.testx
    testy = args.testy

    model = backend_model(model_path, trainx, trainy, testx, testy)
    model.summary()

    weight_file = args.weight

    if weight_file:
        record_files = [f for f in os.listdir(model_dir) if re.match(r'\d{6}_\d{6}',f)]
        if not record_files:
            print('No weight file found. Skip weight loading step.')
        else:
            weight_file = os.path.join(max(record_files), weight_file)
        if os.path.exists(weight_file):
            model.load(weight_file)

    return model, model_dir, (trainx, trainy, testx, testy)

def train_func(args):
    model, model_dir, (trainx, trainy, testx, testy) = build_model(args)

    # Callback_1
    history_callback = Batch_History()
    str_start_time = args.time if args.time else datetime.now().strftime('%y%m%d_%H%M%S')
    model_result_path = os.path.join(model_dir, str_start_time)
    os.mkdir(model_result_path)
    trainlog_dir = os.path.join(model_result_path,'logs')
    os.mkdir(trainlog_dir)

    # Callback_2
    state_file = os.path.join(model_dir, 'state.json')
    #state_file = "/home/plash/petpen/state.json"
    state_callback = Model_state(state_file,model.config)
    history = model.train(callbacks=[history_callback, state_callback])
    save_history(os.path.join(trainlog_dir,'train_log'), history, history_callback)
    model.save(os.path.join(model_result_path,'weights.h5'))

def validate_func(args):
    model, model_dir, (trainx, trainy, testx, testy) = build_model(args)

    # Callback
    history_callback = Batch_History()
    str_start_time = args.time if args.time else datetime.now().strftime('%y%m%d_%H%M%S')
    model_result_path = os.path.join(model_dir, str_start_time)
    os.mkdir(model_result_path)
    validlog_dir = os.path.join(model_result_path,'logs')
    os.mkdir(validlog_dir)
    loss = model.evaluate()
    # save_history(os.path.join(validlog_dir,'valid_log'), history, history_callback)

def predict_func(args):
    testdata = None # feed some test data
    model, model_dir, _ = build_model(args)
    loss = model.predict(testdata)
