const http = require('http');
const express = require('express');
const axios = require('axios');
const path = require('path');
const cors = require('cors');
const app = express();

const flowObjs = {};
const totals = {};
const reuse = {};

app.use(express.json());
app.use(express.static("express"));
app.use(cors());

app.post('/total', function(req,res){
  console.log('total being sent');
  const flow = req.body.workflow_id;
  totals[flow] = req.body.total;
  reuse[flow] = req.body.reuse;
  console.log(`total emails ${req.body.total} for workflow ${flow}`);
  res.send({success: true});
});
app.post('/flowData', function(req,res){
  console.log('data received');
  // console.log(req.body.topHam);
  flowObjs[req.body.flow_id] = req.body;
  // console.log(`flow ${req.body.flow_id}: `, flowObjs[req.body.flow_id]);
  console.log('count:', totals[req.body.flow_id]-req.body.totalEmails);
  if ((req.body.totalEmails >= totals[req.body.flow_id] - 9) && !reuse[req.body.flow_id]) {
    console.log('terminating flow ', req.body.flow_id);
    const data = {
      workflow_id: req.body.flow_id
    };
    axios.post('http://cluster5-1.utdallas.edu:6000/terminate', data)
    .then((res) => {
      console.log('res:', res.data);
    }).catch((err) => {
      console.error('err:', err);
    });
  }
  res.send({success: true});
});
app.use('/getFlow/:id', function(req,res){
  //console.log('req for flow: ', req.params.id);
  //console.log('keys: ', Object.keys(flowObjs));
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