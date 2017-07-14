module.exports = function(RED) {
    function helloWorld(config) {
        RED.nodes.createNode(this,config);
        var context = this.context();
	this.name = config.name
        var node = this;
        this.on('input', function(msg) {
 	var outMsg = { payload: msg.payload + this.name + "\n"}	
	/*var fs = require('fs');
	var obj = JSON.parse(fs.readFileSync('/Users/me/.node-red/flows_DMID-NB2de-MBP.json', 'utf-8'));
	var res = {
		layers: {} 
	};
	for (var i in obj) {
		if (obj[i]['type'] == 'Convulution') {
			name  = obj[i]['name'];
			res.layers[name] = {type: 'Convolution_1D', params: {filters: 3, kernel_size: 3, strides: 3, activation: obj[i]['methods']}};
		}
	}
	json = JSON.stringify(res);
fs.writeFileSync('/Users/me/.node-red/result.json', json, 'utf-8');
	this.log(res);*/
   	this.log(outMsg.payload); 
        node.send(outMsg);
        
        });
    }
    RED.nodes.registerType("Convulution",helloWorld);
};
