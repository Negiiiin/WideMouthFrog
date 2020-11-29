import time
from socket import *
import sys
import threading
import json
import os
import shutil
import logging
from datetime import *
import base64
import time
import unicodedata
from cryptography.fernet import Fernet

MAXLISTEN = 15
EOF = chr(26)
MAXMSGLEN = 1000
DEFAULTDIR = "./dir"
MINDIRLEN = 2
SERVER_PORT = 9123

time.time()
messages = []
msg_ports = []
sender_ports = []
usernames = []
ports = []
IDs = []


def validate(port):
    if port in ports:
        return True
    return False

def find_port(id):
    return ports[IDs.index(id)]

def find_ID(port):
    return IDs[ports.index(port)]

def generate_key(name):
    key = Fernet.generate_key()
    with open("secret" + str(name) + ".key", "wb") as key_file:
        key_file.write(key)

def normalize(name):
    return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')

def handle_client(socket, address):
    global messages, msg_ports
    msg = socket.recv(MAXMSGLEN)
    if msg[:7] == 'sending':
        generate_key(msg[7:])
        socket.sendall("OK")
        msg2 = socket.recv(MAXMSGLEN).decode().split()
        print(find_port(normalize(msg2[1])))
        port = find_port(normalize(msg2[1]))
        msg_ports.append(port)
        messages.append(normalize(msg2[2]))
        sender_ports.append(msg[7:])
    elif msg[:9] == 'listening':
        generate_key(msg[9:])
        port = find_port(msg[9:])
        while True:
            if str(port) in msg_ports:
                message = str(str(time.time()) + " " + str(find_ID(sender_ports[msg_ports.index(port)])) + " " + messages[msg_ports.index(port)])
                encoded_message = message.encode()
                socket.sendall(encoded_message)
                break


def readConfig():
    global usernames, ports, IDs

    file = open ('config.json', "r") 
    config = json.loads(file.read())

    for i in config['users']: 
        usernames.append(normalize(i['username']))
        ports.append(normalize(i['port']))
        IDs.append(normalize(i['ID']))

    file.close()
    return

# ----------------------------------------------------------------------------------------------------------

listenSocket = socket(AF_INET, SOCK_STREAM)
listenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listenSocket.bind(("", SERVER_PORT))
listenSocket.listen(MAXLISTEN)

readConfig()
print(usernames)
while True:
    try:
        socket, address = listenSocket.accept()
        t = threading.Thread(target = handle_client, args = (socket, address))
        t.setDaemon(True)
        t.start()
    except KeyboardInterrupt:
        print("got Keyboard interrupt in main Program!")
        listenSocket.close()
        sys.exit()