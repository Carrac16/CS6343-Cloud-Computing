import socketserver
import socket
import re
from email import policy
from email.parser import BytesParser
import io
import json
from time import sleep
import datetime


FORWARD_HOST = 'spamdetection'
FORWARD_PORT = 5002

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

s = None
connected = False

while not connected:
    try:
        print(f'[+] Connecting to {FORWARD_HOST}:{FORWARD_PORT}')
        s = socket.socket()
        s.connect((FORWARD_HOST, FORWARD_PORT))
        connected = True
    except Exception as e:
        print(f'Could not connect. Trying again in 1 second...')
        sleep(1)

class serverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        dataRead = True
        self.data = ''
        message_count = 0
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
                    s.sendall(f'{"END":<7s}'.encode())
                    return

                text = data['email']
                workflow = data['workflow']

                # do text processing on email
                subject, text = processEmail(text.encode())

                # recreate json with subject/workflow id
                message = json.dumps({'flow_id': workflow, 'email': text, 'subject': subject})
                message = f'{len(message):<6d} {message}'

                # send to spam detection
                s.sendall(message.encode())
                message_count += 1
            else:
                print(f'Sent {message_count} messages')
                s.sendall(f'{"END":<7s}'.encode())
                break


server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), serverHandler)
print('[+] Starting email receiver server')
server.serve_forever()
