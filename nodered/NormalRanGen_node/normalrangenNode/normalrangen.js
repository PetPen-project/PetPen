module.exports = function(RED) {
    function normalrangen_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("NormalRanGen",normalrangen_go);
};
