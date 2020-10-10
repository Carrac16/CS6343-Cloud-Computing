'use strict';

const express = require('express');
const bodyParser = require('body-parser');
const routes = require('./addEmails');

const app = express();

const port = 8080;

app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
app.use('/api', routes);

app.listen(process.env.port || port , () => {
    console.log(`listening for requests on port ${port}`);
});