module.exports = function(RED) {
    function avgpool2d_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("AvgPooling2D",avgpool2d_go);
};
