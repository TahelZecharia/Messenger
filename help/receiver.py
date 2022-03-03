import socket
import os
import sys
import time

# 40.74.129.169 -> azure ip
ServerIP = ''
ServerPORT = 5005

buff = 1024
current_size = 0
ACK = 0
first_frame = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ServerIP, ServerPORT))

data, addr = sock.recvfrom(buff)

fileName, total_size, window_size = data.split("|||")
window_size = int(window_size)
last_frame = first_frame + window_size - 1
window = [None] * window_size

frame_buffer = [None] * window_size
print("Received File : ", fileName)
f = open(fileName, 'wb')

total_size = int(total_size)


def calc_checksum(c_data):
    c_sum = 0

    for i in c_data[1:len(c_data) - 1]:
        c_sum += ord(i)
    c_sum = ~c_sum
    return '%1X' % (c_sum & 0xF)


while True:
    index = 0
    for i in range(first_frame, last_frame + 1):
        window[index] = i
        index += 1

    data, addr = sock.recvfrom(buff)

    current_size += len(data) - 2
    rate = round(float(current_size) / float(total_size) * 100, 2)

    if data[len(data) - 1] == str(calc_checksum(data)):
        print("receive cheksum : ", data[len(data) - 1], " / calculate checksum : ", calc_checksum(data))
        print("no error")

    if current_size > total_size:
        current_size = total_size
    print(current_size, "/", total_size, rate, "%\n")
    f.write(data[1:len(data) - 2])
    if current_size == total_size:
        print("Success")
        sys.exit()

    if first_frame is int(data[0]):
        if first_frame is window_size * 2:
            first_frame %= window_size * 2

        first_frame += 1
        last_frame = first_frame + window_size - 1

    print(window)

    frame_buffer[window.index(int(data[0]))] = data
    ACK = "ACK" + data[0]
    sock.sendto(ACK, addr)

    if None not in frame_buffer:
        for i in frame_buffer:
            f.write(i)
            frame_buffer[frame_buffer.index(i)] = None

sock.close()
f.close()
