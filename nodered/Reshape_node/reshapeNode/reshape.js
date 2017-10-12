module.exports = function(RED) {
    function reshape_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("Reshape",reshape_go);
};
