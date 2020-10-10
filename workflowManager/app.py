#!/usr/bin/env python

from flask import Flask, request  # , request
import docker

app = Flask(__name__)

client = docker.from_env()
replicas = 3


class Task:
    def __init__(self, image, command, name):
        self.image = image
        self.command = command
        self.name = name


workflow1 = [Task('matthewp76/spamdetection', 'python ./spamdetection.py', 'spamdetection')]


'''
def getContainers():
    return client.services.list()


def startService(task):
    return client.services.create(task.image, task.command, name=task.name).scale(replicas=replicas)


@app.route('/', methods=['POST'])
def workflow():
    desiredWorkflow = request.form['workflow']
    inputData = request.form['input']
    return 'Hello World!'


@app.route('/')
def hello():
    return 'This is my flask application!'
'''


@app.route('/post', methods=['POST'])
def post_route():
    if request.method == 'POST':

        data = request.get_json(force=True)  # always try to parse data as JSON

        workflow_list = data['workflow']
        print(f'workflow list: {workflow_list}')

        for component in workflow_list:
            client.services.create(**component).scale(replicas=replicas)
            print(f'Started service {component["image"]} with {replicas} replicas')

        print('Data Received: "{data}"'.format(data=data))
        return "Request Processed.\n"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
