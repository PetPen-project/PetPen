module.exports = function(RED) {
    function maxpool_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("MaxPooling1D",maxpool_go);
};
