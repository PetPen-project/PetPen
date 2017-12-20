module.exports = function(RED) {
    function helloWorld(config) {
        RED.nodes.createNode(this,config);
        var context = this.context();
	this.name = config.name
        var node = this;
        this.on('input', function(msg) {
        node.send(msg);
        
        });
    }
    RED.nodes.registerType("Convolution",helloWorld);
};
