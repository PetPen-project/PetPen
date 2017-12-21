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
	for (var ind in obj) {
		if (obj[ind]['type'] == 'Convulution') {
			name  = obj[ind]['name'] + "_" + ind + "_" +  timest;
			res.layers[name] = {type: 'Convolution_1D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: parseInt(obj[i]['kernel']), strides: parseInt(obj[ind]['strides']), activation: obj[ind]['methods']}};
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
			res.layers[name] = {type: 'CONVOLUTION_2D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: kernels, strides: parseInt(stride_num), activation: obj[ind]['activation']}};
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
			res.layers[name] = {type: 'CONVLSTM_2D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: kernels, strides: parseInt(stride_num), activation: obj[ind]['activation'], padding: obj[ind]['padding'], recurrent_activation: obj[ind]['recurrent_activation'], return_sequence: obj[ind]['return_sequence'], dropout: parseInt(obj[ind]['dropout']), recurrent_dropout: obj[ind]['recurrent_dropout']}};
			rec[obj[ind]['id']] = name;
            		obj[ind]['name'] = name;
		} else if (obj[ind]['type'] == 'Output') {
			name = obj[ind]['name'] + "_" + ind + "_" + timest;
			features = obj[ind]['feature'].split(',');
			res.layers[name] = {type: 'Output', params: {loss: obj[ind]['loss'], optimizer: obj[ind]['optimizer'], epoch: parseInt(obj[ind]['epoch']), batchsize: parseInt(obj[ind]['batchsize'])}};
			res.dataset[name] = features;
			/*var fs = require('fs')
			var filename = '';
			if (fs.existsSync('./file.name')) {
			  filename = fs.readFileSync('./file.name')
			} else {
			  filename = 'tmp.csv'
			  filepath = 'file.name'
 			  fs.writeFile(filepath, filename, (err) => {
    				if (err) throw err;
    				console.log("The name file was succesfully saved!");
			  }); 
			}
			res.dataset['output'] = filename;*/
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

        } else if (obj[ind]['type'] == 'Merge') {
			name = obj[ind]['name'] + "_" + ind + "_" + timest;
			res.layers[name] = {type: 'Merge', params: {activation: obj[ind]['method']}}; 
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
			res.layers[name] = {type: 'Dropout', params: {rate: parseInt(obj[ind]['rate'])}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Gru') {
			name = obj[ind]['name'] + "_" + ind + "_" + timest;
			res.layers[name] = {type: 'Gru', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation']}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'File') {
		path = obj[ind]['file'];
		//var fst = require('fs');
		//var content = fst.readFileSync(path, 'utf-8')
		//fst.writeFileSync("./data.csv", content, 'utf8');
		console.log("myfile");
		console.log(path);
	} else if (obj[ind]['type'] == 'Pretrained') {
		name = obj[ind]['name'] + "_" + ind + "_" + timest;
		res.layers[name] = {type: 'Pretrained', params: {project_name: obj[ind]['source'], nodes: obj[ind]['pretrainedoutput'], weight_file: obj[ind]['weightfile']}};
		rec[obj[ind]['id']] =name;
		obj[ind]['name'] = name;
 	} else if (obj[ind]['type'] == 'Flatten') {
	    name = obj[ind]['name'] + "_" + ind + "_" + timest;
	    res.layers[name] = {type: 'Flatten'};                      
	    rec[obj[ind]['id']] =name;            
	    obj[ind]['name'] = name; 
	}
         

	}
	console.log("now");
	for (var i in obj) {
		name = obj[i]['name'];
		if (obj[i]['wires'] == null) {
//		    console.log(obj[i]['wires']);
        	} else if (name != ""){
			tmp = obj[i]['wires'];
            		res_t = []
            		for (var ii = 0; ii < tmp.length; ii++) {
                		for (var jj = 0; jj < tmp[ii].length; jj++) {
		            		res_t.push(rec[tmp[ii][jj]]);
                		}
            		}
            		if (res_t.length > 0) {
		    		res.connections[name] = res_t;
            		}
        	}	
    	}
	json = JSON.stringify(res);
//      fs.writeFileSync('/home/kazami/.node-red/result.json', json, 'utf-8');
        fs.writeFileSync('result.json', json, 'utf-8');
	var fs = require('fs');
	var obj = '';
	if (fs.existsSync('.child.json')) {
	  obj = fs.readFileSync('child.json', 'utf-8');
	}
	/*var kill = function(pid, signal, callback) {
	  signal = signal || 'SIGKILL';
	  callback = callback || function() {};
	  var killTree = true;
	  if (killTree) {
	    psTree(pid, function(err, children) {
	      [pid].concat(
		  children.map(function (p) {
		    return p.PID;
		  })
		).forEach(function (tpid) {
		    try { process.kill(tpid, signal)}
		    catch (ex) {}
		});
		callback();
	    });
	  } else {
	    try { process.kill(pid, signal) }
	    catch (ex) { }
	    callback();
	  }
	};
	kill(previous_pid);*/
	console.log(obj)
	if (obj >= 1) {
	var exec = require('child_process').exec;
	var arg1 = "-d . ";
	var arg2 = "-n demo1";
	var newproc = exec('python /home/plash/petpen/develop/petpen0.1.py ' + arg1 + ' ' + arg2 + ' ', function(error, stdout, stderr) {
		if (stdout.length > 1) {
			console.log('offer', stdout);
		} else {
			console.log('don\'t offer');
		}
	});
	console.log(newproc.pid);
        fs.writeFileSync('pid.json', newproc.pid, 'utf-8');
	}
	
        node.send(msg);
        
	});

    }
    RED.nodes.registerType("Output",output_go);
};
