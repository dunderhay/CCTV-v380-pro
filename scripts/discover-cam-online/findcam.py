#!/usr/bin/python3
import binascii
import socket
import sys

DEVICEID = sys.argv[1]
SERVER = '47.74.66.18'
PORT = 8900

hexID = bytes(DEVICEID, 'utf-8').hex()

data = 'ac000000f3030000'
data += hexID
data += '2e6e766476722e6e657400000000000000000000000000006022000093f5d10000000000000000000000000000000000'
data = bytes.fromhex(data)

# print (f'Trying device id: {DEVICEID}') #debugging
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))
sock.send(data)
response = sock.recv(4096)
sock.close()

# print('Received Data: ', response)
if response[4] == 1:
    print (f'\u001b[32m[+] Camera with device ID: {DEVICEID} is online!\u001b[37m')
else:
    # print (f'\u001b[31m[-] Camera with device ID: {DEVICEID} is offline.\u001b[37m') #debugging
    pass