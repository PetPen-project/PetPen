module.exports = function(RED) {
    function convlstm2d_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("ConvolutionLSTM_2D",convlstm2d_go);
};
