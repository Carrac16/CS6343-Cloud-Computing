const express = require('express');
const router = express.Router();

const assert = require('assert');
const cassandra = require('cassandra-driver');

const contactPoints = ['10.176.67.94', 'cluster5-1.utdallas.edu'];
const client = new cassandra.Client({contactPoints: contactPoints, localDataCenter: 'datacenter1'});
let client2;

client.execute("Create Keyspace If Not Exists email_space with Replication = { 'class': 'SimpleStrategy', 'replication_factor': 1 }", [], {prepare: true}, function(err, result) {
        if (err) {
                console.log('error creating keyspace', err);
        } else {
                console.log('email_space keyspace created or already exists');
                client2 = new cassandra.Client({contactPoints: contactPoints, keyspace: 'email_space', localDataCenter: 'datacenter1'});
        }
});
client.shutdown();

const getQuery = "Select * From emails;";
const flowQuery = "Select * From emails Where flow_id = ?;";
const addQuery = "Insert into emails (id, flow_id,  sender, subject, content, is_spam) values (?, ?, ?, ?, ?, ?);";
const createQuery = "Create Columnfamily emails (id text, flow_id text, sender text, subject text, content text, is_spam boolean, Primary Key(id));";
const removeQuery = "Truncate emails;";
const dropQuery = "Drop Columnfamily If Exists emails;";

router.get('/dropTable', (req, res) => {
        client2.execute(dropQuery, [], {prepare: true}, function (err, result) {
                if (err) {
                        console.log('error dropping table: ', err);
                        res.send({error: err});
                } else {
                        console.log('table dropped');
                        res.send({success: true});
                }
                return;
        });
});


router.get('/clearTable', (req, res) => {
        client2.execute(removeQuery, [], {prepare: true}, function (err, result) {
                if (err) {
                        console.log('error clearing table: ', err);
                        res.send({error: err});
                } else {
                        console.log('table cleared');
                        res.send({success: true});
                }
                return;
        });
});

router.get('/createTable', (req, res) => {
        client2.execute(createQuery, [], {prepare: true}, function(err, result) {
                if (err) {
                        console.log('error creating table: ', err);
                        res.send({error: err});
                } else {
                        console.log('table created');
                        res.send({success: true});
                }
                return;
        });
});
router.get('/queryEmails', (req, res) => {
        client2.execute(getQuery, [], {prepare: true}, function(err, result) {
                if (err) {
                        console.log('error on query: ', err);
                        res.send({error: err});
                        return;
                } else {
                        for (let i = 0; i < result.rowLength; i++) {
                                console.log(`row ${i} result: `, result.rows[i]);
                        }
                        res.send(result.rows);
                        return result;
                }
        });
});

router.post('/queryEmailFlow', (req, res) => {
        client2.execute(flowQuery, [req.body.flow_id], {prepare: true}, function(err, result) {
                if (err) {
                        console.log('error querying from flow: ', err);
                        res.send({error: err});
                        return;
                } else {
                        for (let i = 0; i < result.rowLength; i++) {
                                console.log(`row ${i} result: `, result.rows[i]);
                        }
                        res.send(result.rows);
                        return result;
                }
        });
});

router.post('/addEmail', (req, res) => {
        client2.execute(addQuery, [req.body.id, req.body.flow_id,  req.body.sender, req.body.subject, req.body.content, req.body.is_spam], {prepare: true}, function(err, result) {
                if (err) {
                        console.log('error adding email to db: ', err);
                        res.send({error: err});
                } else {
                        console.log('email added to db');
                        res.send({success: true});
                }
                return;
        });
});

module.exports = router;
//console.log('connected to Cassandra db');

// function execute(query, params, callback) {
// //   return new Promise((resolve, reject) => {
// //           client.execute(query, params, (err, result) => {
// //                   if (err) {
// //                           reject();
// //                   } else {
// //                           callback(err, result);
// //                           resolve();
// //                   }
// //           });
// //   });
// // }
//
// // let query = "Insert into emails (email_id, content, recieve_date, sender, spam, subject) values (1003430, 'This is spam.', '2020-10-1', 'some1@spam.com', true, 'Do NOT Open');";
//let query2 = "Select * From emails;";
// // let q1 = execute(query, null, (err, result) => {assert.ifError(err); console.log('added row to db.')});
// // let q2 = execute(query2, null, (err, result) => {assert.ifError(err); console.log('result: ', result.rows[0])});
// // Promise.all([q1, q2]).then(() => {
// //   console.log('exiting');
// //   process.exit();
// // });

//client.execute(query2, [], {prepare: true}, function(err, result) {
//      if (err) {
//              console.log('error received:', err);
//      } else {
//              console.log('success: ', result);
//      }
//});