module.exports = function(RED) {
    function conv2d_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("Convolution_2D",conv2d_go);
};
