const http = require('http');
const express = require('express');
const path = require('path');
const app = express();

const flowObjs = {};

app.use(express.json());
app.use(express.static("express"));

app.post('/flowData', function(req,res){
  // console.log(req.body.topHam);
  flowObjs[req.body.flow_id] = req.body;
  // console.log(`flow ${req.body.flow_id}: `, flowObjs[req.body.flow_id]);
  res.send({success: true});
});
app.use('/getFlow/:id', function(req,res){
  if (req.params.id in flowObjs)
    res.send(flowObjs[req.params.id]);
  else
    res.send({error: true});
});
// default URL for website
app.use('/', function(req,res){
  res.sendFile(path.join(__dirname+'/express/index.html'));
  //__dirname : It will resolve to your project folder.
});
const server = http.createServer(app);
const port = 3000;
server.listen(port);
console.debug('Server listening on port ' + port);