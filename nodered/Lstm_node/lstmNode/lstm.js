module.exports = function(RED) {
    function lstm_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("Lstm",lstm_go);
};
