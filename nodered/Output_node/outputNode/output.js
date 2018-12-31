module.exports = function(RED) {
  function output_go(config) {
    RED.nodes.createNode(this,config);
    var node = this;
    this.on('input', function(msg) {
    function iterationCopy(src) {
  	target = {};
  	for (prop in src) {
    	  if (src.hasOwnProperty(prop)) {
      	    target[prop] = src[prop];
    	  }
  	}
  	return target;
    }
      var fs = require('fs');
      var date = new Date();
      var timest = date.getTime();
      if (fs.existsSync('flows_petpen.json')) {
        var obj = JSON.parse(fs.readFileSync('flows_petpen.json', 'utf-8'));
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
      var subids = {}; 
      var subflows_object = {}
      for (var ind in obj) {
        if (obj[ind]['type'] == 'Convolution') {
          name = obj[ind]['name'] + "_" + ind + "_" +  timest;
          res.layers[name] = {type: 'Conv1D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: parseInt(obj[i]['kernel']), strides: parseInt(obj[ind]['strides']), activation: obj[ind]['methods']}};
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
	} else if (obj[ind]['type'] == 'subflow') {
	  name =  "subreplace" + ind + "_" + timest;
	  input = obj[ind]['in'][0]['wires'][0]['id'];
	  output = obj[ind]['out'][0]['wires'][0]['id'];
	  subflows_object[obj[ind]['id']] = [input, output]
	  subids[obj[ind]['id']] = {}
	  rec[obj[ind]['id']] = name;
	  obj[ind]['name'] = name;
	} else if (obj[ind]['type'].substr(0, 8) == 'subflow:') {

		console.log("subflow.....")
	  name =  obj[ind]['type'] + "_" + ind + "_" + timest;
	  scope = obj[ind]['type'].substr(8, 21)
	  subids[scope][obj[ind]['id']] = obj[ind]['type'].substr(8)
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
          res.layers[name] = {type: 'Conv2D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: kernels, strides: parseInt(stride_num), activation: obj[ind]['activation'], padding: obj[ind]['padding']}};
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
          name = obj[ind]['name'] + "_" + ind + "_" + timest;
          datasetname = obj[ind]['datasetname'].split(',');
          res.layers[name] = {type: 'Output', params: {loss: obj[ind]['loss'], optimizer: obj[ind]['optimizer'], epoch: parseInt(obj[ind]['epoch']), batchsize: parseInt(obj[ind]['batchsize']), learningrate: parseFloat(obj[ind]['learningrate'])}};
          res.dataset[name] = datasetname;
          rec[obj[ind]['id']] = name;
          obj[ind]['name'] = name;
        } else if (obj[ind]['type'] === 'Input') {
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
        } else if (obj[ind]['type'] == 'Activation') {
          name = obj[ind]['name'] + "_" + ind + "_" + timest;
          res.layers[name] = {type: 'Activation', params: {activation: obj[ind]['activation']}}; 
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
        } else if (obj[ind]['type'] == 'AvgPooling2D') {
          name = obj[ind]['name'] + "_" + ind + "_" + timest;
          pool_size_arr = obj[ind]['poolsize'].split(',');
          for (var i = 0; i < pool_size_arr.length; i++) {
            pool_size_arr[i] = parseInt(pool_size_arr[i]);
          }
          strides_arr = obj[ind]['strides'].split(',');
          for (var i = 0; i < strides_arr.length; i++) {
            strides_arr[i] = parseInt(strides_arr[i]);
          }
          res.layers[name] = {type: 'AveragePooling2D', params: {strides: strides_arr, pool_size: pool_size_arr, padding: obj[ind]['padding']}};
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
      if (obj[ind]['axis'] != "") {
        axis = parseInt(obj[ind]['axis']);
      } else {
        axis = -1;
      }

	    res.layers[name] = {type: 'BatchNormalization', params: {axis: axis}};
	    rec[obj[ind]['id']] = name;
	    obj[ind]['name']= name;
	}
         
	}
	flow_in = false
	console.log("before parse result")
	console.log("subflow id...")
	console.log(subids)    
	console.log("subflow object...")
	console.log(subflows_object)
	console.log("start parse....")
	prev = null
	for (var key in subflows_object) {
	  console.log("first....")
          console.log(key)
	  var num = 0;
	  for (var subid_key in subids[key]) {
	    console.log("second....")
	    console.log(subid_key)
	    if (num != 0) {
	      console.log(num)
	      console.log(subid_key)
	      var terminate = false
	      var sec = null;
              var timest2 = date.getTime();
	      while (terminate == false) {
	        console.log("third....")
	      	for (var x in obj) {
	          if (flow_in == false && obj[x]['id'] == subflows_object[key][0]) {
		    console.log("input")
		    console.log(obj[x])
		    tmp = null
		    tmp = JSON.parse(JSON.stringify(obj[x]))
		    tmp['id'] = Math.random().toString(36).substr(2, 9) 
	            name = tmp['name'] + "_" + Math.random().toString(36).substr(2, 9);
		    console.log(name)
		    tmp['name'] = name
	            res.layers[name] = iterationCopy(res.layers[obj[x]['name']]);
	            rec[tmp['id']] = name;
		    len = obj.length
		    obj.push(tmp)
		    sec = Math.random().toString(36).substr(2, 9)	
		    subids[key][subid_key] = sec 
		    subflows_object[sec] = []
		    subflows_object[sec].push(tmp['id'])
		    prev = len 
		    flow_in = true
		    break;
	    } else if (flow_in == true && prev != null && obj[prev]['wires'][0][0] == obj[x]['id'] && obj[x]['id'] == subflows_object[key][1]) {
		    console.log("output");
		    console.log(obj[x])
		tmp = null
		tmp = JSON.parse(JSON.stringify(obj[x]))
		tmp['id'] = Math.random().toString(36).substr(2, 9) 
	        name = tmp['name'] + "_" + Math.random().toString(36).substr(2, 9);
		tmp['name'] = name
	        res.layers[name] = iterationCopy(res.layers[obj[x]['name']]);
	        rec[tmp['id']] = name;
		  obj.push(tmp)
		  subflows_object[sec][1] = tmp['id']
		  sec = null;
		obj[prev]['wires'][0][0] = tmp['id']
		  flow_in = false
		  terminate = true
		    break;
	    } else if (prev != null && prev != null && flow_in == true && obj[prev]['wires'][0][0] == obj[x]['id']) {
		    console.log("continue")
		    console.log(obj[x])
		    console.log(prev)
		tmp = null
		tmp = JSON.parse(JSON.stringify(obj[x]))
		tmp['id'] = Math.random().toString(36).substr(2, 9) 
	        name = tmp['name'] + "_" + Math.random().toString(36).substr(2, 9);
		tmp['name'] = name
	        res.layers[name] = iterationCopy(res.layers[obj[x]['name']]);
	        rec[tmp['id']] = name;
		len = obj.length
		obj.push(tmp)
	json_obj = JSON.stringify(obj);
        fs.writeFileSync('object1.json', json_obj, 'utf-8');
		obj[prev]['wires'][0][0] = tmp['id']
	json_obj = JSON.stringify(obj);
        fs.writeFileSync('object2.json', json_obj, 'utf-8');
		    console.log(obj[prev])
		  prev = len
		    break;
	    }
	    }
	  }

	  }
		  num = num + 1;
	}
	}
 	console.log("parse result")
	console.log(res.layers)
	console.log(subids)    
	console.log("subflows")
	console.log(subflows_object)
	console.log("parse finish...")
	    
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
			var target = null
            		for (var ii = 0; ii < tmp.length; ii++) {
                		for (var jj = 0; jj < tmp[ii].length; jj++) {
					var found = false;
					for (var domain in subids) {
					  if (tmp[ii][jj] in subids[domain]) {
						console.log(typeof(subids[domain][tmp[ii][jj]]))
						input_node = subflows_object[subids[domain][tmp[ii][jj]]]
						console.log(subflows_object)
						console.log(subids[tmp[ii][jj]])
						console.log(rec[input_node[0]]);
						res_t.push(rec[input_node[0]]);
						found = true;
					  } 
					}
					if (found == false) {
		            		res_t.push(rec[tmp[ii][jj]]);
					}
                		}
            		}
            		if (res_t.length > 0) {
				var found = false;
				for (var domain in subids) {
				  if (obj[i]['id'] in subids[domain]) {
					console.log("is this....")
					console.log(obj[i])
					output_node = subflows_object[subids[domain][obj[i]['id']]][1]
					res.connections[rec[output_node]] = res_t;
					found = true;
				  }
				}
				  if (found == false) {
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
