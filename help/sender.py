import os
import socket
import sys
import time

ServerIP = sys.argv[1]
ServerPORT = int(sys.argv[2])
filePath = sys.argv[3]
window_size = sys.argb[4]
# 40.74.129.169 -> azure ip
#ServerIP = '40.74.129.169'
#ServerPORT = 5005
#filePath = '/home/u201203406/Desktop/Hello/packet.py'
addr = (ServerIP, ServerPORT)

buff = 1024
frameNumber = 0
current_size = 0
#window_size = 4
window = [None] * window_size
frame_buffer = [None] * window_size * 2
first_frame = 0
last_frame = first_frame+window_size - 1
boolean_ACK = [False] * window_size

if window_size > 5:
    print('Window size is smaller than 5')
    sys.exit()

if len(sys.argv) < 4:
    print('[Dest IP Addr] [ Dest Port] [File Path] [Window Size]')
    sys.exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
fileName = os.path.basename(filePath)
fileSize = os.path.getsize(filePath)
data = fileName + "|||" + str(fileSize) + "|||" + str(window_size)

sock.settimeout(2)

sock.sendto(data, addr)
f = open(filePath, 'rb')


def calc_checksum(c_data):
    c_sum = 0

    for i in c_data:
        c_sum += ord(i)
    c_sum = ~c_sum
    return '%1X' % (c_sum & 0xF)

while True:
    index = 0
    try:

        for i in range(first_frame, last_frame+1):
            window[index] = i
            index += 1

        data = f.read(buff - 2)
        print("send checksum : ", calc_checksum(data))
        data = str(frameNumber) + data + str(calc_checksum(data))
        frame_buffer[frameNumber] = data
        sock.sendto(frame_buffer[frameNumber], addr)
        frameNumber += 1
        if frameNumber is window_size*2:
            frameNumber %= window_size*2

        current_size += len(data)-2

        if current_size > fileSize:
            current_size = fileSize

        rate = round(float(current_size) / float(fileSize) * 100, 2)
        print(current_size, "/", fileSize, rate, "%\n")
        if current_size == fileSize:
            print("Success")
            sys.exit()

        print(window)

        ACK, address = sock.recvfrom(buff)
        if "ACK" in ACK:
            if int(ACK[3]) is first_frame:
                if first_frame is window_size*2:
                    first_frame %= window_size*2
                first_frame += 1
                last_frame = first_frame + window_size-1

            print("received ACK number is ", ACK[3])
            boolean_ACK[window.index(int(ACK[3]))] = True

    except socket.timeout:
        print("Time out")
        for i in range(first_frame, last_frame+1):
            if boolean_ACK[i] is False:
                sock.sendto(frame_buffer[window.index(i)], addr)

sock.close()
f.close()
