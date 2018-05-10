from keras.models import Model, load_model
from keras.utils.np_utils import to_categorical
from keras.utils import plot_model
import keras.layers
import numpy as np
import pandas as pd
import json, os, pickle, re

def load_csv(data):
    result = pd.read_csv(data, header=None).values
    return np.array(result)

def load_pkl(data):
    try:
        result = pickle.load( open(data, 'rb') )
    except:
        result = pd.read_pickle(data)
    return np.array(result)

def load_npy(data):
    result = np.load(data)
    return result

def load_file(f):
    if '.csv' in f:
        return load_csv(f)
    elif '.pkl' in f or '.pickle' in f:
        return load_pkl(f)
    elif 'npy' in f:
        return load_npy(f)

class backend_model():
    def __init__(self, model_path, trainx, trainy, testx, testy):
        self.load_dataset(trainx, trainy, testx, testy)
        self.model, self.config, self.inputs, self.outputs = self.get_model(model_path)
        self.loss = self.config.get('loss') or None
        self.optimizer = self.config.get('optimizer') or None

        if 'entropy' in self.loss:
            self.model.compile(loss=self.loss, optimizer=self.optimizer, metrics=['acc'])
        else:
            self.model.compile(loss=self.loss, optimizer=self.optimizer)

        self.batch_size = self.config.get('batch_size') or self.config.get('batchsize')
        self.epochs = self.config.get('epochs') or self.config.get('epoch')
        self.callbacks = []

    def load_dataset(self, train_input, train_output, test_input, test_output):
        if train_input or train_output or test_input or test_output:
            self.get_data_from_json = False
            if '.csv' in train_input:
                self.train_x, self.train_y, self.valid_x, self.valid_y = load_csv(train_input), load_csv(train_output), load_csv(test_input), load_csv(test_output)
            elif '.pkl' in train_input or '.pickle' in train_input:
                self.train_x, self.train_y, self.valid_x, self.valid_y = load_pkl(train_input), load_pkl(train_output), load_pkl(test_input), load_pkl(test_output)
        else:
            self.get_data_from_json = True
            self.train_x, self.train_y, self.valid_x, self.valid_y = [], [], [], []

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

    def summary(self):
        self.model.summary()

    def plot_model(self, file_name='model.png'):
        plot_model(self.model, to_file=file_name)

    def set_callbacks(self, callbacks):
        self.callbacks = callbacks

    def set_batch_size(self, batch_size):
        self.batch_size = batch_size

    def save(self, file_path):
        self.model.save(file_path)

    def load(self, file_path):
        self.model.load_model(file_path)

    def get_model(self, model_file):
        """
        read model setting from given model json file, then parse to keras model
        """

        # Read JSON
        with open(model_file) as f:
            model_parser = json.load(f)
        connections = model_parser['connections']
        layers = model_parser['layers']
        dataset = model_parser['dataset']
        # Check connections
        if len(connections.keys()) < len(layers.keys())-1:
            raise ValueError('some components are not connected!')

        # Gather inputs
        inputs = list(filter(lambda layer_name: layers[layer_name]['type']=='Input', layers))
        if self.get_data_from_json:
            for i in inputs:
                self.train_x.append(load_file(dataset[i]['train_x']))
                self.valid_x.append(load_file(dataset[i]['valid_x']))

        # Prepared for return values
        input_names = inputs
        output_names = []

        # Check if inputs are given
        if not inputs:
            raise ValueError('missing input layer in the model')

        # Translate inputs into keras layers
        model_inputs = []
        created_layers = {}
        for nn_in in inputs:
            input_params = layers[nn_in]['params']
            created_layers[nn_in] = deserialize_layer(layers[nn_in], name=nn_in)
            model_inputs.append(created_layers[nn_in])

        # Gather merge layers (didn't check)
        merges = filter(lambda layer_name: layers[layer_name]['type']=='Merge', layers)
        merge_nodes = {m:[] for m in merges}
        for node in merge_nodes:
            inbound_nodes = list(map(lambda connection: connection[0],filter(lambda connection: node in connection[1], connections.items())))
            if len(inbound_nodes) <= 1:
                raise ValueError('merge layer {} needs more than one inbound nodes'.format(node))
            merge_nodes[node]=inbound_nodes
        # WARN: Above code-block didn't check

        # Iteratively create layer objects
        model_output = []
        while inputs:
            print(inputs)
            next_layers = []
            for conn_in in inputs:
                conn_outs = connections[conn_in]
                for conn_out in conn_outs:
                    if conn_out in created_layers:
                        # Already translated
                        continue
                    layer_config = layers[conn_out]

                    layer_type, layer_params = layers[conn_out]['type'], layers[conn_out].get('params',{})


                    # Merge layers (didn't check)
                    if layer_type.lower() == 'merge':
                        inbound_node_names = merge_nodes[conn_out]
                        if set(inbound_node_names).issubset(created_layers.keys()):
                            layer = deserialize_layer(layer_config, name=conn_out)
                            inbound_nodes = [created_layers[node] for node in inbound_node_names]
                            created_layers[conn_out] = layer(inbound_nodes)
                            next_layers.append(conn_out)
                        else:
                            next_layers.append(conn_in)
                    # WARN: Above code-block didn't check


                    elif layer_type.lower() == 'output':
                        model_output.append(created_layers[conn_in])
                        config = layer_params
                        output_names.append(conn_out)
                        if self.get_data_from_json:
                            self.train_y.append(load_file(dataset[conn_out]['train_y']))
                            self.valid_y.append(load_file(dataset[conn_out]['valid_y']))

                    elif layer_type.lower() == 'pretrained':
                        pretrained_model = load_pretrained_model(layer_params)
                        created_layers[conn_out] = pretrained_model(created_layers[conn_in])
                        next_layers.append(conn_out)

                    else:
                        layer = deserialize_layer(layer_config, name=conn_out)
                        inbound_node = created_layers[conn_in]
                        created_layers[conn_out] = layer(inbound_node)
                        next_layers.append(conn_out)

            inputs = next_layers

        model_output = model_output or []
        if not model_output:
            raise ValueError('missing output in model')

        model = Model(inputs=model_inputs, outputs=model_output)

        return model, config, input_names, output_names

def load_pretrained_model(layer_config):
    output_layer = int(layer_config['nodes'])-1
    model_file = str(layer_config['weight_file'])
    trainable = int(layer_config['trainable'])

    pretrained_model = load_model(model_file)

    model = Model(
        inputs=pretrained_model.input,
        outputs=pretrained_model.layers[output_layer].output
    )

    if not trainable:
        for layer in model.layers:
            layer.trainable = False

    return model

def deserialize_layer(layer_config, name=None):
    layer_type = layer_config.get('type')
    if layer_type is None:
        raise ValueError('Undefined layer type')
    layer_params = layer_config.get('params',{})

    if not hasattr(keras.layers,layer_type):
        pass

    # need to fix the inconsistent parameter name and values in future
    if layer_type.lower() == 'convlstm2d':
        if 'return_sequence' in layer_params:
            condition = layer_params.pop('return_sequence')
            if condition == 'True':
                layer_params['return_sequences'] = True
            else:
                layer_params['return_sequences'] = False
    elif layer_type.lower() == 'lstm' or layer_type.lower() == 'simplernn':
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
        merge_method = layer_params['method']
        return getattr(keras.layers, merge_method)
    layer = getattr(keras.layers,layer_type)(name = name,**layer_params)
    return layer

if __name__ == '__main__':
    model, config, inp, oup = get_model('data/3/include_pretrain/result.json')
    model.compile(loss=config.get('loss'), optimizer=config.get('optimizer'))
    model.summary()

