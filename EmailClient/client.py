import socket
import os
import random
import sys
import json
from time import sleep


if len(sys.argv) != 3:
    print('Error! Expected "./client.py <number of test cases> <workflow_number>"', file=sys.stderr)
    exit(0)

FORWARD_HOST = 'emailserver'
FORWARD_PORT = 5001
num_tests = int(sys.argv[1])
workflow_num = int(sys.argv[2])

BUFFER_SIZE = 4096

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

print(f'[+] Sending {num_tests} test emails')

num_ham = 0
num_spam = 0

for _ in range(num_tests):
    if random.randint(0, 1) == 1:
        file_dir = 'spam'
        num_spam += 1
    else:
        file_dir = 'ham'
        num_ham += 1
    filename = f'./test_data/{file_dir}/{random.choice(os.listdir("./test_data/" + file_dir))}'

    with open(filename, 'r', errors='ignore') as f:
        file_content = json.dumps({'workflow': workflow_num, 'email': f.read()})
        file_content = f'{len(file_content):<6d} {file_content}'


        try:
            s.sendall(file_content.encode())
        except BrokenPipeError as err:
            print(f'Broken pipe error')
            s = socket.socket()
            s.connect((FORWARD_HOST, FORWARD_PORT))
            s.sendall(file_content.encode())

        # print(f'content: {file_content}')


s.close()

print('[+] Connected.')

print(f'[+] Sent {num_ham} ham, {num_spam} spam tests')
