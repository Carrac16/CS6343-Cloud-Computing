import socket
import os
import random
import sys
import json
from time import sleep
import requests
import webbrowser
from flask import Flask

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print('Error! Expected "./client.py <number of test cases> <workflow id - optional>"', file=sys.stderr)
    exit(0)

num_tests = int(sys.argv[1])
workflow_filename = 'workflow.json'

if len(sys.argv) == 3:
    workflow_id = sys.argv[2]
else:
    workflow_id = None

print(f'[+] Sending {num_tests} test emails')

num_ham = 0
num_spam = 0

if not workflow_id:
    with open(workflow_filename, 'r') as f:
        data = json.loads(f.read())
    print(f'Requesting workflow')
    x = requests.post(f'http://cluster5-1.utdallas.edu:6000/start', json=data)
    # print(f'x: {x.text}')
    response = json.loads(x.text)
    print(f'response: {response}')
    entrypoint = response['entrypoint']
    workflow_id = response['workflow_id']

else:
    print(f'Using workflow {workflow_id}')
    with open(workflow_filename, 'r') as f:
        data = json.loads(f.read())
    data['workflow_id'] = workflow_id
    x = requests.post(f'http://cluster5-1.utdallas.edu:6000/start', json=data)
    response = json.loads(x.text)
    print(f'response: {response}')
    entrypoint = response

print(f'[+] Open http://cluster5-2.utdallas.edu:3000?flow={workflow_id} to view results')

# send workflow id and number of emails to webpage
with open(workflow_filename, 'r') as f:
        data = json.loads(f.read())

webpage_data = {'workflow_id': workflow_id, 'total': num_tests, 'reuse': data['workflow']['reuse']}

x = requests.post(f'http://cluster5-2.utdallas.edu:3000/total', json = webpage_data)


if entrypoint['requestType'] == 'POST':
    # get address components
    forward_host = entrypoint['address']
    forward_port = entrypoint['port']
    endpoint = entrypoint['endpoint'] if 'endpoint' in entrypoint else '/'

for _ in range(num_tests):
    if random.randint(0, 1) == 1:
        file_dir = 'spam'
        num_spam += 1
    else:
        file_dir = 'ham'
        num_ham += 1
    filename = f'./test_data/{file_dir}/{random.choice(os.listdir("./test_data/" + file_dir))}'

    with open(filename, 'r', errors='ignore') as f:
        file_content = json.dumps({'flow_id': workflow_id, 'content': f.read()})

        # send to first component
        success = False
        while not success:
            try:
                x = requests.post(f'{forward_host}:{forward_port}{endpoint}', json=file_content)
                success = True
            except requests.exceptions.ConnectionError as e:
                print(f'Waiting for services to start...')
                sleep(2)


print(f'[+] Sent {num_ham} ham, {num_spam} spam tests on workflow {workflow_id}')
