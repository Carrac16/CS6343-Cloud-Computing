import socket
import os
import random
import sys

SEPARATOR = " "
BUFFER_SIZE = 4096

host = "192.168.1.231"
port = 5001

if len(sys.argv) != 4:
    print('Error! Expected "./client.py <hostname> <port> <number of test cases>"', file=sys.stderr)
    exit(0)

host = sys.argv[1]
port = int(sys.argv[2])
num_tests = int(sys.argv[3])

# filesize = os.path.getsize(filename)


print(f'[+] Connecting to {host}:{port}')
print('[+] Connected.')

num_ham = 0
num_spam = 0

for _ in range(num_tests):
    s = socket.socket()
    s.connect((host, port))
    if random.randint(0, 1) == 1:
        file_dir = 'spam'
        num_spam += 1
    else:
        file_dir = 'ham'
        num_ham += 1
    filename = f'./test_data/{file_dir}/{random.choice(os.listdir("./test_data/" + file_dir))}'

    bytes_read = True
    with open(filename, 'r', errors='ignore') as f:
        while bytes_read:
            bytes_read = f.read(BUFFER_SIZE).encode()
            if not bytes_read:
                break
            s.sendall(bytes_read)
    s.close()

print(f'[+] Sent {num_ham} ham, {num_spam} spam tests')
