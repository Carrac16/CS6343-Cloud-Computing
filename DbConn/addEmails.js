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
const addQuery = "Insert into emails (id, sender, subject, content, is_spam) values (?, ?, ?, ?, ?);";
const createQuery = "Create Columnfamily emails (id text, sender text, subject text, content text, is_spam boolean, Primary Key(id));";
const removeQuery = "Truncate emails;";

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

router.post('/addEmail', (req, res) => {
        client2.execute(addQuery, [req.body.id, req.body.sender, req.body.subject, req.body.content, req.body.is_spam], {prepare: true}, function(err, result) {
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
