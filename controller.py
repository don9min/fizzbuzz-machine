#!/usr/bin/python3

import socket
import time
import random
import sys

print("*** START CONTROLLER ***")
if len(sys.argv) == 1:
    err_prob = 0.5
else:
    err_prob = float(sys.argv[1])

host = socket.gethostname()
port = 51002
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.87.107', port))
    msg = s.recv(1024)
    recv_str = msg.decode('ascii')
    print("Received number:" + recv_str)
    number = int(recv_str)
    if number % 15 == 0: 
        if random.random() > err_prob:
            s.send(str(3).encode())
            print("Just sent a command 3")
        else:
            s.send(str(100).encode())
            print("Transmission error occurs")
    elif number  % 5 == 0:
        if random.random() > err_prob:
            s.send(str(2).encode())
            print("Just sent a command 2")
        else:
            s.send(str(100).encode())
            print("Transmission error occurs")
    elif number  % 3 == 0: 
        if random.random() > err_prob:
            s.send(str(1).encode())
            print("Just sent a command 1")
        else:
            s.send(str(100).encode())
            print("Transmission error occurs")
    else: 
        if random.random() > err_prob:
            s.send(str(0).encode())
            print("Just sent a command 0")
        else:
            s.send(str(100).encode())
            print("Transmission error occurs")
    time.sleep(0.5) # 5 sec wait
    s.close()
