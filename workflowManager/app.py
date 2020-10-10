#!/usr/bin/env python

from flask import Flask, request
import docker
from docker.types import EndpointSpec

app = Flask(__name__)

client = docker.from_env()
replicas = 3

deployed_services = []

def deployed(object):
    for service in deployed_services:
        if service["image"] == object["image"]:
            return True
    return False

@app.route('/start', methods=['POST'])
def start_workflow():
    if request.method == 'POST':

        data = request.get_json(force=True)  # always try to parse data as JSON

        workflow_list = data['workflow']
        print(f'workflow list: {workflow_list}')

        already_deployed = []

        for component in workflow_list:
            if not deployed(component):
                endpoint_spec = None
                if "port" in component:
                    port = component.pop("port")
                    endpoint_spec = EndpointSpec(ports={port:port})
                client.services.create(**component, endpoint_spec=endpoint_spec).scale(replicas=replicas)
                deployed_services.append(component)
                print(f'Started service {component["image"]} with {replicas} replicas')
            else:
                already_deployed.append(component["image"])
                print(f'Service {component["image"]} has already been started')

        print('Data Received: "{data}"'.format(data=data))
        if already_deployed:
            return f"Services were already deployed: {already_deployed}\n"
        return "Request Processed.\n"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
