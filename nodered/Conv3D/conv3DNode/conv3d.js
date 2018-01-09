module.exports = function(RED) {
    function conv3d_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("Conv3D",conv3d_go);
};
