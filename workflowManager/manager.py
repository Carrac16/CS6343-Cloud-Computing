#!/usr/bin/env python

from flask import Flask, request

import docker

app = Flask(__name__)

client = docker.env()

replicas = 3

class Task:
    def __init__(self, image, command, name):
        self.image = image
        self.command = command
        self.name = name

workflow1 = [Task('kbouguyon/spamdetector', 'python ./3NB2.py', 'spamdetector')]

def getContainers():
    return client.services.list()

def startService(task):
    return client.services.create(
        task.image,
        task.command,
        name=task.name,
    ).scale(replicas)


@app.route('/', methods=['POST'])
def workflow():
    desiredWorkflow = request.form['workflow']
    inputData = request.form['input']
    return 'Hello World!'
# spin up containers needed

# pass data through containers
