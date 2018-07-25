module.exports = function(RED) {
  function activation_go(config) {
    RED.nodes.createNode(this,config);
    var node = this;
    this.on('input', function(msg) {
      node.send(msg);
    });
  }
  RED.nodes.registerType("Activation",activation_go);
};
