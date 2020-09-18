#!/usr/bin/python3
import socket
import time

ADVERTISE_INTERVAL = 10
IP_ADDR = '255.255.255.255'
PORT = 10008

listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen_sock.bind(('',10009))

last_advertise_at = 0
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    if (time.time() - last_advertise_at) >= ADVERTISE_INTERVAL:
        # nvdevsearch packet
        data = '4e564445565345415243485e3130300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        data = bytes.fromhex(data)
        print ('[*] Looking for IP Camera on the local network...')
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        send_sock.sendto(data, (IP_ADDR, PORT))
        last_advertise_at = time.time()

        try:
            listen_sock.settimeout(9)
            result = (listen_sock.recvfrom(4096, 0))[0]
            print (f'\u001b[32m[+] Camera found: {result}\u001b[37m')
        except socket.timeout:
            continue

# To find group devices use:
# nvgroupsearch = '4e5647524f55505345415243485e3130305e3000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
