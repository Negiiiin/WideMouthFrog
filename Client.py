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

def generate_key(name):
    key = Fernet.generate_key()
    with open("secret" + str(name) + ".key", "wb") as key_file:
        key_file.write(key)

def load_key(name):
    return open("secret" + str(name) + ".key", "rb").read()

def decrypt_message(encrypted_message, name):
    key = load_key(name)
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()

def encrypt_message(message, name):
    key = load_key(name)
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message

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
    while msg != "listen" and msg != "send":
        print("wrong command !")
        msg = raw_input("your message: ")
    if msg == "listen":
        socket.sendall("listening" + id)
        print("Listening ...")
        msg = socket.recv(MAXMSGLEN)
        msg = decrypt_message(msg, id).split()
        print("The key is: " + str(normalize(msg[2])) + " From client with ID: " + str(normalize(msg[1])))
        if normalize(msg[1]) < time.time() - TIME_LIMIT:
            print("BUT THE KEY IS INVALID")
    elif msg == "send":
        socket.sendall("sending" + id)
        msg = socket.recv(MAXMSGLEN)
        if msg == 'OK':
            load_key(id)
            msg = raw_input("your dst ID: ")
            key = str(Fernet.generate_key())
            message = str(str(time.time()) + " " + msg + " " + key)
            print(id, "\n\n")
            encoded_message = encrypt_message(message, id)
            socket.sendall(encoded_message)
            print("Key " + str(key) + " is sent to client with ID " + str(msg))

except KeyboardInterrupt:
    socket.close()
    sys.exit()

socket.close()