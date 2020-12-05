import socket
import re
from email import policy
from email.parser import BytesParser
import io
import json
import datetime
import requests
from flask import Flask, request

app = Flask(__name__)


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001

BUFFER_SIZE = 4096
SEPARATOR = " "


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial


def processEmail(emailBytes):
    try:
        msg = BytesParser(policy=policy.default).parse(io.BytesIO(emailBytes))
        text = msg.get_body(preferencelist=('plain')).get_content()
        text = emailBytes.decode()
    except Exception as e:
        text = emailBytes.decode()

    lines = text.split('\n')
    if 'Subject:' in lines[0]:
        subject = lines[0][8:]
    else:
        subject = ''

    if subject != '':
        text = ' '.join(lines)
    else:
        text = ' '.join(lines[1:])
    # print(f'Pre-formatted text: {text}')
    text = re.sub(r'https?://\S+', '', text, flags=re.MULTILINE)  # remove links
    text = re.sub(r' +|\t+|\\n', ' ', text)  # remove unnecessary spaces
    text = re.sub(r'\s([,?.!"](?:\s|$))', r'\1', text)  # remove spaces before punctuation
    # print(f'Text: {text}')

    # Check if text is empty before forwarding

    return subject, text


def get_next_components(workflow_id):
    x = requests.post('http://cluster5-1.utdallas.edu:6000/next', data=json.dumps({'workflow_id': workflow_id, 'service_name': 'emailserver'}))
    response = json.loads(x.text.replace('\'', '"'))
    print(f'response: {response}')
    return response


next_components = {}


@app.route('/', methods=['POST'])
def recieve_email():
    if request.method == 'POST':
        data = request.get_json(force=True)  # always try to parse data as JSON
        data = json.loads(str(data))
        workflow_id = data['flow_id']
        text = data['content']

        # do text processing on email
        subject, text = processEmail(text.encode())

        # recreate json with subject/workflow id
        message = json.dumps({'flow_id': workflow_id, 'content': text, 'subject': subject})

        # get next address to forward to
        if workflow_id not in next_components:
            next_components[workflow_id] = get_next_components(workflow_id=workflow_id)


        for component in next_components[workflow_id]:
            if component['requestType'] == 'POST':
                forward_host, forward_port = component['address'], component['port']
                endpoint = component['endpoint'] if 'endpoint' in component else '/'

                # send post request
                x = requests.post(f'{forward_host}:{forward_port}{endpoint}', json=message)

                print(f'Forwarded to {forward_host}:{forward_port}{endpoint}, workflow: {workflow_id}')

    return ""


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT)

'''class serverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        dataRead = True
        self.data = ''
        message_count = 0
        next_components = {}

        while True:
            # read message size
            message_size = self.request.recv(7).decode()
            if len(message_size) > 1:
                # read message
                dataRead = self.request.recv(int(message_size)).decode()
                self.data = dataRead

                # load json from message
                try:
                    data = json.loads(self.data)
                except json.decoder.JSONDecodeError as decode_error:
                    # print('Error decoding JSON. Skipping.')
                    # s.sendall(f'{"END":<7s}'.encode())
                    return

                text = data['email']
                workflow = data['workflow']

                # do text processing on email
                subject, text = processEmail(text.encode())

                # recreate json with subject/workflow id
                message = json.dumps({'flow_id': workflow, 'email': text, 'subject': subject})
                message = f'{len(message):<6d} {message}'

                # get next address to forward to
                if workflow not in next_components:
                    next_components[workflow] = get_next_components(workflow_id=workflow)
                components = next_components[workflow]
                for component in components:
                    if component['requestType'] == 'NONE':
                        forward_host, forward_port = component['address'], component['port']
                        s = socket.socket()
                        s.connect((forward_host, forward_port))
                        s.sendall(message.encode())
                        s.close()
                        print(f'Forwarded to {forward_host}, {forward_port}')


                # send to spam detection
                # s.sendall(message.encode())
                message_count += 1
            else:
                print(f'Sent {message_count} messages')
                # s.sendall(f'{"END":<7s}'.encode())
                break


server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), serverHandler)
print('[+] Starting email receiver server')
server.serve_forever()'''
