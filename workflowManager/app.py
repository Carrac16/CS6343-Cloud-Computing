#!/usr/bin/env python

from datetime import datetime
import docker
from docker.types import EndpointSpec
from flask import Flask, request
import uuid
import re

app = Flask(__name__)

client = docker.from_env()
replicas = 3

deployed_workflows = {}

def log(workflow_id, message):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"[{timestamp}] {workflow_id} : {message}")

def deploy_component(workflow_id, component):
    endpoint_spec = None
    if "port" in component:
        port = component.pop("port")
        endpoint_spec = EndpointSpec(ports={port:port})
    if "publishedPort" in component and "targetPort" in component:
        publishedPort = component.pop("publishedPort")
        targetPort = component.pop("targetPort")
        endpoint_spec = EndpointSpec(ports={publishedPort:targetPort})
    log(workflow_id, f"Starting component {component['name']} with {replicas} replicas")
    client.services.create(**component, endpoint_spec=endpoint_spec).scale(replicas=replicas)
    log(workflow_id, f"Service {component['name']} is now available")

def deployed(object):
    return bool(client.services.list(filters={ "name": object["name"] }))

def get_next_services(wfid, current):
    workflow = deployed_workflows[wfid]
    if not workflow:
        return []

    for component in workflow['components']:
        if component['service']['name'] == current:
            return component['next']
        else: # check if the root of the service name matches, since new services need different names than the old ones
            reg = re.compile(current+".+")
            match = bool(re.match(reg, component['service']['name']))
            if match:
                return component['next']

    return []


@app.route('/start', methods=['POST'])
def start_workflow():
    if request.method == 'POST':

        data = request.get_json(force=True)  # always try to parse data as JSON
        if 'workflow_id' in data:
            wfid = data['workflow_id']
            if wfid in deployed_workflows:
                return deployed_workflows[wfid]['entrypoint']
            else:
                return { "error": f"Workflow with ID ({wfid}) does not exist" }

        if 'workflow' in data:
            workflow = data['workflow']
            workflow_id = str(uuid.uuid4())
            entrypoint = workflow['entrypoint']
            reuse = workflow['reuse']
            workflow_list = workflow['components']
            log(workflow_id, f"Workflow requested.")

            for component in workflow_list:
                service = component['service']
                if not deployed(service) or not reuse:
                    deploy_component(workflow_id, service)

            deployed_workflows[workflow_id] = { "components": workflow_list, "entrypoint": entrypoint }

            log(workflow_id, f"Workflow deployed.")
            return { "workflow_id": workflow_id, "entrypoint": entrypoint }
        
        return { "error": "User must specify a workflow or a workflow ID" }


@app.route('/next', methods=['POST'])
def next_service():
    if request.method == 'POST':
        data = request.get_json(force=True)

        workflow_id = data['workflow_id']
        current_service = data['service_name']

        log(workflow_id, f"{current_service} is requesting the next service.")

        return str(get_next_services(workflow_id, current_service))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
