import os
import pcapy as p
from scapy.all import *
from scapy.layers.http import *
from scapy.sessions import *
from scapy.sendrecv import sniff
import re
import pyshark
import time
from socket import *
import threading
import sys
import os
import unicodedata
import time

MAXLISTEN = 15
MAXMSGLEN = 1000
TIME_LIMIT = 10

socket = socket(AF_INET, SOCK_STREAM)
try :
    socket.connect(("", 9123))
except error:
    print("500 could not establish connection to server")
    socket.close()
    sys.exit()

listener = ""
sender = ""
keys = []
packets = rdpcap('pcaps/in2.pcap')
for packet in packets:
    if packet.haslayer(TCP):
        if packet.haslayer(Raw):
            if "listening" in packet[Raw].load.decode():
                listener = packet[Raw].load.decode()[9:]
            elif "sending" in packet[Raw].load.decode():
                sender = packet[Raw].load.decode()[7:]
            if packet[TCP].sport == 9123 and packet.haslayer(Raw):
                if packet[Raw].load.decode() != "OK" and packet[Raw].load.decode() not in keys:
                    keys.append(packet[Raw].load)
print(keys)

                    
last_one_used = 0
while True:
    socket.sendall(("sending" + listener).encode())
    msg = socket.recv(MAXMSGLEN)
    print(msg)
    if msg.decode() == 'OK':
        message = keys[last_one_used]
        last_one_used += 1
        print(id, "\n\n")
        socket.sendall(message)
        print("Send message from listener to sender")

    print("HEYYYYYYYYYYYY")
    socket.sendall(("listening" + sender).encode())
    msg = socket.recv(MAXMSGLEN)
    keys.append(msg)
    print("Recieved message from listener")

    t = time.time()
    while time.time() - t < 5:
        continue

    socket.sendall(("sending" + sender).encode())
    msg = socket.recv(MAXMSGLEN)
    print(msg)
    if msg.decode() == 'OK':
        message = keys[last_one_used]
        last_one_used += 1
        print(id, "\n\n")
        socket.sendall(message)
        print("Send message from sender to listener")

    socket.sendall(("listening" + listener).encode())
    msg = socket.recv(MAXMSGLEN)
    keys.append(msg)
    print("Recieved message from sender")
    print(keys)
    