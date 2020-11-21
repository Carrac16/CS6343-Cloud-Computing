#!/usr/bin/env python

import docker
from docker.types import EndpointSpec
from flask import Flask, request
import uuid

app = Flask(__name__)

client = docker.from_env()
replicas = 3

deployed_workflows = {}

def get_workflow(wfid):
    for workflow in deployed_workflows:
        if workflow['id'] == wfid:
            return workflow
    return False

def deploy_component(component):
    endpoint_spec = None
    if "port" in component:
        port = component.pop("port")
        endpoint_spec = EndpointSpec(ports={port:port})
    client.services.create(**component, endpoint_spec=endpoint_spec).scale(replicas=replicas)
    print(f'Started service {component["image"]} with {replicas} replicas')

def deployed(object):
    return bool(client.services.list(filters={ "name": object["name"] }))

def get_next_services(wfid, current):
    workflow = deployed_workflows[wfid] # get_workflow(wfid)
    if not workflow:
        return []

    for component in workflow:
        if component['service']['name'] == current:
            return component['next']

    return []


@app.route('/start', methods=['POST'])
def start_workflow():
    if request.method == 'POST':

        data = request.get_json(force=True)  # always try to parse data as JSON
        workflow = data['workflow']
        workflow_id = str(uuid.uuid4())
        entrypoint = workflow['entrypoint']
        workflow_list = workflow['components']
        print(f'workflow list: {workflow_list}')

        for component in workflow_list:
            service = component['service']
            if not deployed(service):
                deploy_component(service)

        deployed_workflows[workflow_id] = workflow_list

        return { "workflow_id": workflow_id, "entrypoint": entrypoint }


@app.route('/next', methods=['POST'])
def next_service():
    if request.method == 'POST':
        data = request.get_json(force=True)

        workflow_id = data['workflow_id']
        current_service = data['service_name']

        return str(get_next_services(workflow_id, current_service))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
