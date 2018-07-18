module.exports = function(RED) {
  function output_go(config) {
    RED.nodes.createNode(this,config);
    var node = this;
    this.on('input', function(msg) {
      var fs = require('fs');
      console.log("ff")
      console.log("test for new")
      var date = new Date();
      var timest = date.getTime();
      if (fs.existsSync('flows_ubuntu.json')) {
        var obj = JSON.parse(fs.readFileSync('flows_ubuntu.json', 'utf-8'));
      } else {
        console.log("flow not exist");
        return;
      }
      var res = {
        layers: {},
        connections: {}, 
        dataset: {},
      };
      var rec = {};
      var input = null 
      var output = null 
      var subid = null 
      for (var ind in obj) {
        console.log(obj[ind]);
        if (obj[ind]['type'] == 'Convolution') {
          name = obj[ind]['name'] + "_" + ind + "_" +  timest;
          res.layers[name] = {type: 'Conv1D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: parseInt(obj[i]['kernel']), strides: parseInt(obj[ind]['strides']), activation: obj[ind]['methods']}};
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'subflow') {
          console.log(obj[ind]);
          name =  "subreplace";
          input = obj[ind]['in'][0]['wires'][0]['id'];
          output = obj[ind]['out'][0]['wires'][0]['id'];
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
        } else if (obj[ind]['type'].substr(0, 8) == 'subflow:') {
          name =  obj[ind]['type'] + "_" + ind + "_" + timest;
          subid = obj[ind]['id']
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Conv3D') {
          name = obj[ind]['name'] + "_" + ind + "_" + timest;
          kernels = obj[ind]['kernel'].split(",");
          for (var i = 0; i < kernels.length; i++) {
            kernels[i] = parseInt(kernels[i]);
          }
          stride_num = obj[ind]['strides'].split(",");
          for (var i = 0; i < stride_num.length; i++) {
            stride_num[i] = parseInt(stride_num[i]);
          }
          res.layers[name] = {type: 'Conv3D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: kernels, strides: stride_num, padding: obj[ind]['padding'], activation: obj[ind]['activation']}};
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Convolution_2D') {
          name  = obj[ind]['name'] + "_" + ind + "_" + timest;
          kernels = obj[ind]['kernel'].split(",");
          for (var i = 0; i < kernels.length; i++) {
            kernels[i] = parseInt(kernels[i]);
          }
          stride_num = obj[ind]['strides'].split(",");
          for (var i = 0; i < stride_num.length; i++) {
            stride_num[i] = parseInt(stride_num[i]);
          }
          res.layers[name] = {type: 'Conv2D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: kernels, strides: parseInt(stride_num), activation: obj[ind]['activation']}};
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'ConvolutionLSTM_2D') {
          name  = obj[ind]['name'] + "_" + ind + "_" + timest;
          kernels = obj[ind]['kernel'].split(",");
          for (var i = 0; i < kernels.length; i++) {
            kernels[i] = parseInt(kernels[i]);
          }
          stride_num = obj[ind]['strides'].split(",");
          for (var i = 0; i < stride_num.length; i++) {
            stride_num[i] = parseInt(stride_num[i]);
          }
          res.layers[name] = {type: 'ConvLSTM2D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: kernels, strides: parseInt(stride_num), activation: obj[ind]['activation'], padding: obj[ind]['padding'], recurrent_activation: obj[ind]['recurrent_activation'], return_sequence: obj[ind]['return_sequence'], dropout: parseFloat(obj[ind]['dropout']), recurrent_dropout: parseFloat(obj[ind]['recurrent_dropout'])}};
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'Output') {
          console.log(obj[ind]['datasetname']);
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                datasetname = obj[ind]['datasetname'].split(',');
                res.layers[name] = {type: 'Output', params: {loss: obj[ind]['loss'], optimizer: obj[ind]['optimizer'], epoch: parseInt(obj[ind]['epoch']), batchsize: parseInt(obj[ind]['batchsize']), learningrate: parseFloat(obj[ind]['learningrate'])}};
                res.dataset[name] = datasetname;
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] === 'Input') {
                console.log(obj[ind]);
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                shapes = obj[ind]['shape'].split(',');
                features = obj[ind]['feature'].split(',');
                for (var ii = 0; ii < shapes.length; ii++) {
                  shapes[ii] = parseInt(shapes[ii]);
                }
                res.layers[name] = {type: 'Input', params: {shape: shapes}}; 
                res.dataset[name] = features;
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'Dense') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                res.layers[name] = {type: 'Dense', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation']}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'ZeroPadding') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                var dimension = parseInt(obj[ind]['dimension']);
                var padding = [];
                if (obj[ind]['padding'].split(',').length==1){
                  for (var i = 0; i < dimension; i++){
                    var num = parseInt(obj[ind]['padding']);
                    padding[i] = [num, num];
                  }
                } else if (obj[ind]['padding'].match(/(\([0-9]+,[0-9]+\))/)){
                  var matched = obj[ind]['padding'].match(/(\([0-9]+,[0-9]+\))/g);
                  for (var i = 0; i < dimension; i++){
                    padding[i] = matched[i].match(/(\d)/g).map(function(item, index, array){return parseInt(item);});
                  }
                } else {
                  var nums = obj[ind]['padding'].split(',');
                  for (var i = 0; i < dimension; i++){
                    padding[i] = [nums[i],nums[i]];
                  }
                }
                res.layers[name] = {type: 'ZeroPadding', params: {padding: padding, dimension: dimension}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'Reshape') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                shapes = obj[ind]['shape'].split(',');
                for (var i = 0; i < shapes.length; i++) {
                  shapes[i] = parseInt(shapes[i]);
                }
                res.layers[name] = {type: 'Reshape', params: {shape: shapes}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'MaxPooling2D') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                pool_size_arr = obj[ind]['poolsize'].split(',');
                for (var i = 0; i < pool_size_arr.length; i++) {
                  pool_size_arr[i] = parseInt(pool_size_arr[i]);
                }
                strides_arr = obj[ind]['strides'].split(',');
                for (var i = 0; i < strides_arr.length; i++) {
                  strides_arr[i] = parseInt(strides_arr[i]);
                }
                res.layers[name] = {type: 'MaxPooling2D', params: {strides: strides_arr, pool_size: pool_size_arr, padding: obj[ind]['padding']}};
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;

              } else if (obj[ind]['type'] == 'MaxPooling1D') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                pool_size = parseInt(obj[ind]['poolsize']);
                strides = parseInt(obj[ind]['strides']);
                res.layers[name] = {type: 'MaxPooling1D', params: {strides: strides, pool_size: pool_size, padding: obj[ind]['padding']}};
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'Merge') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                res.layers[name] = {type: 'Merge', params: {method: obj[ind]['method'], axis: obj[ind]['axis']}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'SimpleRNN') {
                name = obj[ind]['name'] + "_" + ind;
                res.layers[name] = {type: 'SimpleRNN', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation']}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'Lstm') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                res.layers[name] = {type: 'Lstm', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation'], return_sequence: obj[ind]['return_sequence']}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'Dropout') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                res.layers[name] = {type: 'Dropout', params: {rate: parseFloat(obj[ind]['rate'])}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'Gru') {
                name = obj[ind]['name'] + "_" + ind + "_" + timest;
                res.layers[name] = {type: 'Gru', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation']}}; 
                rec[obj[ind]['id']] = name;
                obj[ind]['name'] = name;
              } else if (obj[ind]['type'] == 'File') {
          path = obj[ind]['file'];
          console.log("myfile");
          console.log(path);
        } else if (obj[ind]['type'] == 'Pretrained') {
          name = obj[ind]['name'] + "_" + ind + "_" + timest;
          res.layers[name] = {type: 'Pretrained', params: {project_name: obj[ind]['source'], nodes: obj[ind]['pretrainedoutput'], weight_file: obj[ind]['weightfile'], trainable: obj[ind]['trainable']}};
          rec[obj[ind]['id']] =name;
          obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Flatten') {
            name = obj[ind]['name'] + "_" + ind + "_" + timest;
            res.layers[name] = {type: 'Flatten', params: {}};                      
            rec[obj[ind]['id']] =name;            
            obj[ind]['name'] = name; 
        } else if (obj[ind]['type'] == 'BatchNormalization') {
            name = obj[ind]['name'] + "_" + ind + "_" + timest;
            res.layers[name] = {type: 'BatchNormalization', params: {axis: obj[ind]['axis']}};
            rec[obj[ind]['id']] = name;
            obj[ind]['name']= name;
        }
      }
	    console.log(subid);
      for (var i in obj) {
        name = obj[i]['name'];
        if (obj[i]['wires'] == null) {
          if (obj[i]['name'] == 'subreplace') {
            input = obj[i]['in'][0]['wires'][0]['id'];
            output = obj[i]['out'][0]['wires'][0]['id'];
          }
        } else if (name != ""){
          tmp = obj[i]['wires'];
          res_t = []
          if (tmp == subid) {
            res_t.push(rec[input]);
          } else {
            for (var ii = 0; ii < tmp.length; ii++) {
              for (var jj = 0; jj < tmp[ii].length; jj++) {
                if (tmp[ii][jj] == subid) {
                  console.log("wrong")
                  res_t.push(rec[output]);
                } else {
                  res_t.push(rec[tmp[ii][jj]]);
                }
              }
            }
          }
          if (res_t.length > 0) {
            if (obj[i]['id'] == subid) {
              res.connections[rec[output]] = res_t;
            } else {
              res.connections[name] = res_t;
            }
          }
        }	
      }
      json = JSON.stringify(res);
      fs.writeFileSync('result.json', json, 'utf-8');
      node.send(msg);
    });
  }
  RED.nodes.registerType("Output",output_go);
};
