from keras.models import Model
from keras.utils.np_utils import to_categorical
import keras.layers
import numpy as np
import pandas as pd
import json
import os
import pickle

def load_csv(train_input, train_output, test_input, test_output):
    train_x = pd.read_csv(train_input).values
    train_y = pd.read_csv(train_output).values
    valid_x = pd.read_csv(test_input).values
    valid_y = pd.read_csv(test_output).values

    train_x = np.array(train_x)
    train_y = np.array(train_y)
    valid_x = np.array(valid_x)
    valid_y = np.array(valid_y)
    return train_x, train_y, valid_x, valid_y

def load_pkl(train_input, train_output, test_input, test_output):
    train_x = pickle.load( open(train_input, 'rb') )
    train_y = pickle.load( open(train_output, 'rb') )
    valid_x = pickle.load( open(test_input, 'rb') )
    valid_y = pickle.load( open(test_output, 'rb') )

    train_x = np.array(train_x)
    train_y = np.array(train_y)
    valid_x = np.array(valid_x)
    valid_y = np.array(valid_y)
    return train_x, train_y, valid_x, valid_y


class backend_model():
    def __init__(self, model_path):
        self.model,self.config,self.inputs,self.outputs = get_model(model_path)
        self.loss = self.config.get('loss') or None
        self.optimizer = self.config.get('optimizer') or None
        self.model.compile(loss=self.loss, optimizer=self.optimizer)
        self.batch_size = self.config.get('batch_size') or self.config.get('batchsize')
        self.epochs = self.config.get('epochs') or self.config.get('epoch')
        self.callbacks = []

    def load_dataset(self, train_input, train_output, test_input, test_output):
        if '.csv' in dataset_path:
            (self.train_x,
            self.train_y,
            self.valid_x,
            self.valid_y) = load_csv(train_input,
                                    train_output,
                                    test_input,
                                    test_output)

        elif '.pkl' in dataset_path:
            (self.train_x,
            self.train_y,
            self.valid_x,
            self.valid_y) = load_pkl(train_input,
                                    train_output,
                                    test_input,
                                    test_output)

    def train(self,**kwargs):
        callbacks = []
        if 'callbacks' in kwargs:
            callbacks = kwargs['callbacks']
        return self.model.fit(self.train_x, self.train_y,
            batch_size=self.batch_size,
            epochs=self.epochs,
            callbacks=callbacks,
            initial_epoch=0,
            validation_data=(self.valid_x,self.valid_y))

    def evaluate(self,**kwargs):
        return self.model.evaluate(self.valid_x, self.valid_y,
                batch_size=self.batch_size)

    def predict(self,test_data):
        return self.model.predict(test_data)

    def plot_model(self, file_name='model.png'):
        from keras.utils import plot_model
        plot_model(self.model, to_file=file_name)

    def set_callbacks(self,callbacks):
        self.callbacks = callbacks

    def set_batch_size(self,batch_size):
        self.batch_size = batch_size

    def save_weights(self,file_path):
        self.model.save_weights(file_path)

    def load_weights(self,file_path):
        self.model.load_weights(file_path,by_name=True)

    def save_architecture(self,json_fp):
        json_string = self.model.to_json()
        with open(json_fp,'w') as f:
            f.write(json_string)

def get_model(model_file):
    """
    read model setting from given model json file, then parse to keras model
    """

    import json
    import re

    with open(model_file) as f:
        model_parser = json.load(f)
    connections = model_parser['connections']
    layers = model_parser['layers']

    if len(connections.keys()) < len(layers.keys())-1:
        raise ValueError('some components are not connected!')
    created_layers = {}

    # gather inputs
    inputs = list(filter(lambda layer_name: layers[layer_name]['type']=='Input', layers))

    input_names = inputs
    output_names = []

    if len(inputs) == 0:
        raise ValueError('missing input layer in the model')
    for nn_in in inputs:
        input_params = layers[nn_in]['params']
        created_layers[nn_in] = deserialize_layer(layers[nn_in], name=nn_in)
    model_inputs = list(created_layers.values())
    # gather merge layers
    merges = filter(lambda layer_name: layers[layer_name]['type']=='Merge', layers)
    merge_nodes = {m:[] for m in merges}
    for node in merge_nodes:
        inbound_nodes = list(map(lambda connection: connection[0],filter(lambda connection: node in connection[1], connections.items())))
        if len(inbound_nodes) <= 1:
            raise ValueError('merge layer {} needs more than one inbound nodes'.format(node))
        merge_nodes[node]=inbound_nodes

    # iteratively create layer objects
    model_output = []
    while inputs:
        next_layers = []
        for conn_in in inputs:
            conn_outs = connections[conn_in]
            for conn_out in conn_outs:
                if conn_out in created_layers:
                    continue
                layer_config = layers[conn_out]

                layer_type,layer_params = layers[conn_out]['type'], layers[conn_out]['params']
                if layer_type.lower() == 'merge':
                    inbound_node_names = merge_nodes[conn_out]
                    if set(inbound_node_names).issubset(created_layers.keys()):
                        layer = deserialize_layer(layer_config, name=conn_out)
                        inbound_nodes = [created_layers[node] for node in inbound_node_names]
                        created_layers[conn_out] = layer(inbound_nodes)
                        next_layers.append(conn_out)
                    else:
                        next_layers.append(conn_in)
                elif layer_type.lower() == 'output':
                    model_output.append(created_layers[conn_in])
                    config = layer_params
                    output_names.append(conn_out)
                else:
                    layer = deserialize_layer(layer_config, name=conn_out)
                    inbound_node = created_layers[conn_in]
                    created_layers[conn_out] = layer(inbound_node)
                    next_layers.append(conn_out)
        inputs = next_layers
    model_output = model_output or []
    if not model_output:
        raise ValueError('missing output in model')
    model = Model(model_inputs, model_output)
    return model, config, input_names, output_names

def deserialize_layer(layer_config, name=None):
    layer_type = layer_config.get('type')
    if layer_type is None:
        raise ValueError('Undefined layer type')
    layer_params = layer_config.get('params')

    if not hasattr(keras.layers,layer_type):
        pass

    # need to fix the inconsistent parameter name and values in future
    if layer_type.lower() == 'convolution_2d':
        layer_type = 'Conv2D'
    if layer_type.lower() == 'convlstm_2d':
        layer_type = 'ConvLSTM2D'
    if layer_type.lower() == 'lstm' or layer_type.lower() == 'simplernn':
        if layer_type.lower() == 'Lstm':
            layer_type = 'LSTM'
        if 'return_sequence' in layer_params:
            condition = layer_params.pop('return_sequence')
            if condition == 'True':
                layer_params['return_sequences'] = True
        else:
            layer_params['return_sequences'] = False
    elif layer_type.lower() == 'reshape':
        layer_params['target_shape'] = layer_params.pop('shape')
    elif layer_type.lower() == 'merge':
        merge_method = layer_params['activation']
        return getattr(keras.layers, merge_method)
    layer = getattr(keras.layers,layer_type)(name = name,**layer_params)
    return layer

def compile_model(model,**kw_args):
    model.compile(**kw_args)

if __name__ == '__main__':
    model = get_model('models/model.json')
    print(model)
    # compile_model(model,)
