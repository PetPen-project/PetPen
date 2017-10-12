module.exports = function(RED) {
    function file_go(config) {
        RED.nodes.createNode(this,config);
	var node = this;
	this.on('input', function(msg) {
	console.log(msg.req.files);
	var files = msg.req.files;
	var oldpath = files.myUploadedFile[0]["path"];
	var newpath = '/media/disk1/datasets/tmp.csv';
        var fs = require('fs');
	fs.writeFile("./file.name", newpath);
      fs.createReadStream(oldpath).pipe(fs.createWriteStream(newpath));
	//fs.rename(oldpath, newpath, function (err) {
        //if (err) throw err;
        console.log('File uploaded and moved!');
        //});	
        node.send(msg);
        
	});
    }
    RED.nodes.registerType("File",file_go);
};
