module.exports = function(RED) {
    function randomgen_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("RandomGen",randomgen_go);
};
