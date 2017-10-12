module.exports = function(RED) {
    function input_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
	node.send(msg);
	});
    }
    RED.nodes.registerType("Input",input_go);
};
