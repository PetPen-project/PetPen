/**
 * Copyright 2013 IBM Corp.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 **/

module.exports = function(RED) {
  'use strict';
  var poster = require('poster');

  function FileUploadNode(n) {
    RED.nodes.createNode(this, n);
    this.name = n.name;
    this.url = n.url;
    this.file = n.file;
    this.func = n.func;
    var functionText = 'var results = (function(msg){' + this.func + '\n})(msg);';
    this.topic = n.topic;
    var _this = this;

    this.on('input', function(msg) {

      var options = {
        uploadUrl: n.url,
        method: 'POST',
        fileId: 'file',
        fields: {
          'script': '{"file":"%s"}'
        },
        uploadHeaders:{
          'Cookie':((msg.cookie)? msg.cookie : "")
        }
      };

      poster.post(n.file, options, function(err, data) {
        if (!err) {
          msg.payload = data;
          _this.send(msg);
        } else {
          _this.error(err);
        }
      });
    });
  }
  RED.nodes.registerType('file-upload', FileUploadNode);
}
