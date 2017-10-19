module.exports = function(RED) {
    function maxpool2d_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("MaxPooling2D",maxpool2d_go);
};
