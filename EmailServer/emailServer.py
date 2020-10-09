import socketserver
import socket
import re
from email import policy
from email.parser import BytesParser
import io
import sys
import datetime

if len(sys.argv) != 3:
    print('Error! Expected arguments python emailServer.py <spam_detection_host> <spam_detection_port>', file=sys.stderr)
    exit(0)

forward_host = sys.argv[1]
forward_port = int(sys.argv[2])


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

    text = ' '.join(text.split("\n"))
    # print(f'Pre-formatted text: {text}')
    text = re.sub(r'https?://\S+', '', text, flags=re.MULTILINE)  # remove links
    text = re.sub(r' +|\t+|\\n', ' ', text)  # remove unnecessary spaces
    text = re.sub(r'\s([,?.!"](?:\s|$))', r'\1', text)  # remove spaces before punctuation
    # print(f'Text: {text}')

    # Check if text is empty before forwarding

    return text


class serverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        dataRead = True
        self.data = ''
        while dataRead:
            dataRead = self.request.recv(BUFFER_SIZE).decode()
            self.data += dataRead
        print(f'{self.client_address[0]}:{self.client_address[1]} sent a message.')

        # Send formatted text to spamdetection
        s = socket.socket()
        s.connect((forward_host, forward_port))
        s.sendall(processEmail(self.data.encode()).encode())
        s.close()


server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), serverHandler)
print('[+] Starting email receiver server')
server.serve_forever()
