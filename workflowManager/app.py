#!/usr/bin/env python

from flask import Flask, request
import docker

app = Flask(__name__)

client = docker.from_env()
replicas = 3

@app.route('/start', methods=['POST'])
def start_workflow():
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
