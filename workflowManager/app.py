#!/usr/bin/env python

import docker
from docker.types import EndpointSpec
from flask import Flask, request
import uuid

app = Flask(__name__)

client = docker.from_env()
replicas = 3

deployed_workflows = []

def deploy_component(component):
    endpoint_spec = None
    if "port" in component:
        port = component.pop("port")
        endpoint_spec = EndpointSpec(ports={port:port})
    client.services.create(**component, endpoint_spec=endpoint_spec).scale(replicas=replicas)
    print(f'Started service {component["image"]} with {replicas} replicas')

def deployed(object):
    deployed_services = client.services.list()
    for service in deployed_services:
        if service["image"] == object["image"]:
            return True
    return False


@app.route('/start', methods=['POST'])
def start_workflow():
    if request.method == 'POST':

        data = request.get_json(force=True)  # always try to parse data as JSON

        workflow_id = uuid.uuid4()
        workflow_list = data['workflow']
        print(f'workflow list: {workflow_list}')

        for component in workflow_list:
            if not deployed(component):
                deploy_component(compnent)

        deployed_workflows.append({ "id": workflow_id, "workflow": workflow_list })

        print('Data Received: "{data}"'.format(data=data))
        return workflow_id


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
