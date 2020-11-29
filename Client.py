import time
from socket import *
import threading
import sys
import os
import termios
import atexit
from select import select
from cryptography.fernet import Fernet
import unicodedata


MAXLISTEN = 15
MAXMSGLEN = 1000
TIME_LIMIT = 10

def load_key(name):
    return open("secret" + str(name) + ".key", "rb").read()

def normalize(name):
    return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')

server_port = int(sys.argv[1])
id = sys.argv[3]
port = sys.argv[2]

socket = socket(AF_INET, SOCK_STREAM)
socket.bind(("", int(port)))
try :
    socket.connect(("", server_port))
except error:
    print("500 could not establish connection to server")
    socket.close()
    sys.exit()

try:
    msg = raw_input("your message: ")
    if msg == "listen":
        socket.sendall("listening" + id)
        key = load_key(id)
        encoded_message = key.encode()
        msg = socket.recv(MAXMSGLEN).decode().split()
        print("The key is: " + str(normalize(msg[2])) + " From client with ID: " + str(normalize(msg[1])))
        if normalize(msg[1]) < time.time() - TIME_LIMIT:
            print("BUT THE KEY IS INVALID")
    elif msg[:4] == "send":
        socket.sendall("sending" + id)
        msg = socket.recv(MAXMSGLEN)
        print(msg)
        if msg == 'OK':
            load_key(id)
            msg = raw_input("your dst ID: ")
            key = str(Fernet.generate_key())
            message = str(str(time.time()) + " " + msg + " " + key)
            encoded_message = message.encode()
            socket.sendall(encoded_message)
            print("Key " + str(key) + " is sent to client with ID " + str(msg))
except KeyboardInterrupt:
    socket.close()
    sys.exit()