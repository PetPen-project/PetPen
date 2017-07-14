module.exports = function(RED) {
    function output_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
	var fs = require('fs');
	var obj = JSON.parse(fs.readFileSync('flows_plash-SYS-7048GR-TR.json', 'utf-8'));
	var res = {
		layers: {},
		connections: {}, 
	};
        var rec = {};
	for (var ind in obj) {
		if (obj[ind]['type'] == 'Convulution') {
			name  = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'Convolution_1D', params: {filters: parseInt(obj[ind]['filters']), kernel_size: parseInt(obj[i]['kernel']), strides: parseInt(obj[ind]['strides']), activation: obj[ind]['methods']}};
			rec[obj[ind]['id']] = name;
			obj[ind]['name'] = name;
        	} else if (obj[ind]['type'] == 'Convolution_2D') {
			name  = obj[ind]['name'] + "_" + ind;
            		kernels = obj[ind]['kernel'].split(",");
	    		for (var i = 0; i < kernels.length; i++) {
				kernels[i] = parseInt(kernels[i]);
	    		}
            		stride_num = obj[ind]['strides'].split(",");
	    		for (var i = 0; i < stride_num.length; i++) {
				stride_num[i] = parseInt(stride_num[i]);
	    		}
			res.layers[name] = {type: 'CONVOLUTION_2D', params: {filters: parseInt(obj[i]['filters']), kernel_size: kernels, strides: parseInt(stride_num), activation: obj[ind]['methods']}};
			rec[obj[ind]['id']] = name;
            		obj[ind]['name'] = name;
		} else if (obj[ind]['type'] == 'Output') {
			name = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'Output', params: {loss: obj[ind]['loss'], optimizer: obj[ind]['optimizer'], epoch: parseInt(obj[ind]['epoch']), batchsize: parseInt(obj[ind]['batchsize'])}};
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
		} else if (obj[ind]['type'] === 'Input') {
			console.log(rec);
			name = obj[ind]['name'] + "_" + ind;
            		shapes = obj[ind]['shape'].split(',');
			for (var ii = 0; ii < shapes.length; ii++) {
				shapes[ii] = parseInt(shapes[ii]);
			}
			res.layers[name] = {type: 'Input', params: {shape: shapes}}; 
			rec[obj[ind]['id']] = name;
            		obj[ind]['name'] = name;
		} else if (obj[ind]['type'] == 'Dense') {
			name = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'Dense', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation']}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Reshape') {
			name = obj[ind]['name'] + "_" + ind;
            shapes = obj[ind]['shape'].split(',');
	    for (var i = 0; i < shapes.length; i++) {
			shapes[i] = parseInt(shapes[i]);
		}

			res.layers[name] = {type: 'Reshape', params: {shape: shapes}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Merge') {
			name = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'Merge', params: {activation: obj[i]['activation']}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'SimpleRNN') {
			name = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'SimpleRNN', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation']}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Lstm') {
			name = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'Lstm', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation'], return_sequence: obj[ind]['return_sequence']}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Dropout') {
			name = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'Dropout', params: {rate: parseInt(obj[ind]['rate'])}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        } else if (obj[ind]['type'] == 'Gru') {
			name = obj[ind]['name'] + "_" + ind;
			res.layers[name] = {type: 'Gru', params: {units: parseInt(obj[ind]['units']), activation: obj[ind]['activation']}}; 
			rec[obj[ind]['id']] = name;
            obj[ind]['name'] = name;
        }

         

	}
	console.log(obj);
	console.log(res);
	console.log(rec);
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
/*	var exec = require('child_process').exec;
	var arg1 = "5";
	var arg2 = "6";
	exec('python2.7 py_test.py ' + arg1 + ' ' + arg2 + ' ', function(error, stdout, stderr) {
		if (stdout.length > 1) {
			console.log('offer', stdout);
		} else {
			console.log('don\'t offer');
		}
	});
*/	
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("Output",output_go);
};
