module.exports = function(RED) {
    function pretrained_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('pretrained', function(msg) {
	node.send(msg);
	});
    }
    RED.nodes.registerType("Pretrained", pretrained_go);
};
