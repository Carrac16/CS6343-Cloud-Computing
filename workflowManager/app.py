#!/usr/bin/env python

from flask import Flask #, request

# import docker

# manager = Flask(__name__)

# client = docker.DockerClient(base_url='unix://var/run/docker.sock')
# client = docker.DockerClient(base_url='tcp://127.0.0.1:63568')
# client = docker.from_env()
#
# replicas = 3
#
# class Task:
#     def __init__(self, image, command, name):
#         self.image = image
#         self.command = command
#         self.name = name
#
# workflow1 = [Task('kbouguyon/spamdetector', 'python ./3NB2.py', 'spamdetector')]
#
# def getContainers():
#     return client.services.list()
#
# def startService(task):
#     return client.services.create(task.image, task.command, name=task.name).scale(replicas)


# @app.route('/', methods=['POST'])
# def workflow():
#     desiredWorkflow = request.form['workflow']
#     inputData = request.form['input']
#     return 'Hello World!'
# spin up containers needed

# pass data through containers


# health check route
# @manager.route('/')
# def health():
#     return 'I am healthy!'
#
# if __name__ == '__main__':
#     manager.run()

app = Flask(__name__)

@app.route('/')
def hello():
    return 'This is my flask application!'

if __name__ == '__main__':
    app.run()
