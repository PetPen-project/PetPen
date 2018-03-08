module.exports = function(RED) {
    function zeropadding_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("ZeroPadding",zeropadding_go);
};
