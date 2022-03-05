import socket
import threading
import os
from pathlib import Path

"""
In this class we implemented the selective repeat sending protocol.
"""

class Sender:

    def __init__(self, udp_socket, addr, file_name, save_as ):

        self.soc: socket = udp_socket
        self.addr = addr # addr to send the file
        self.file_name = file_name # the name of the file to send
        self.save_as = save_as # the name of the new file
        file = Path(file_name)
        self.file_size = os.path.getsize(file)  # the file size in bytes
        print("size:", self.file_size)

        self.buff = 1024
        self.window_size = 4
        self.start_window = 0
        self.end_window = self.start_window + self.window_size - 1

        self.frame_num = 0
        self.next_frame = 0
        self.frame_buff = [''] * (self.window_size * 2)
        self.curr_size = 0
        self.boolean_ACK = [False] * (self.window_size * 2)

        # 1) sends the file details to client:
        self.send_details()

        # 2) open the file:
        self.f = open(file_name, 'rb')

        # 3)
        self.sender_thread = True
        threading.Thread(target=self.sender_file, args=()).start()


    """
    1)  sends the file details to client and make sure the client receives them. 
    """
    def send_details(self):
        data = f"{self.save_as}|||{str(self.file_size)}|||{str(self.window_size)}".encode('utf-8')
        self.soc.sendto(data, self.addr)
        ACK = ""
        while ACK != "ACK":
            ACK, address = self.soc.recvfrom(self.buff)
            ACK = ACK.decode()
        print("send_details")


    """
    2) This func sends to the client the file with "selective-repeat" protocol.
        the func using with the "receiver_ACK" func to control the receive of the ACK.
    """
    def sender_file(self):

        print("sender_file")
        self.soc.settimeout(2)
        data = self.f.read(self.buff - 1).decode('utf-8')

        while self.sender_thread:

            while data:
                try:

                    print("start window:", self.start_window)
                    print("window frame:", self.frame_buff)

                    flag = False
                    cur = self.start_window
                    for i in range(self.window_size):
                        if cur == self.next_frame:
                            flag = True
                        cur = (self.start_window + 1) % (self.window_size * 2)
                        if flag:
                            if self.frame_buff[self.next_frame] == '':
                                data = str(self.next_frame) + data
                                self.boolean_ACK[self.next_frame] = False
                                self.frame_buff[self.next_frame] = data
                                self.soc.sendto(data.encode('utf-8'), self.addr)
                                self.next_frame = (self.next_frame + 1) % (self.window_size * 2)
                                # self.end_window = (self.start_window + self.window_size - 1) % (self.window_size * 2)
                                print("next frame:", self.next_frame)
                                print(data)
                                data = self.f.read(self.buff - 1).decode('utf-8')

                                self.curr_size += len(data) - 1

                                if self.curr_size >= self.file_size:
                                    self.curr_size = self.file_size
                                    print(self.file_size, "/", self.file_size, 100, "%\n")
                                    print("SSSSSSuccessSSSSS")
                                    break

                                rate = round(float(self.curr_size) / float(self.file_size) * 100, 2)
                                print(self.curr_size, "/", self.file_size, rate, "%\n")

                            self.receiver_ACK()

                except socket.timeout:
                    print("Time out")
                    cur = self.start_window
                    for i in range(self.window_size):
                        if self.boolean_ACK[cur] is False:
                            self.soc.sendto(self.frame_buff[cur].encode('utf-8'), self.addr)
                        cur += 1
                        cur %= self.window_size * 2


            self.f.close()
            print(f"File {self.file_name} Downloaded")
            self.sender_thread = False

    """
    This func receive the ACK from client
    """
    def receiver_ACK(self):

        try:
            print("receiver_ACK")
            ACK, address = self.soc.recvfrom(4)

            if "ACK" in ACK.decode():
                ACK_num = int(ACK.decode()[3])
                print("received ACK number is ", ACK_num)

                cur = self.start_window
                for i in range(self.window_size):
                    if ACK_num == cur:
                        print("cur", cur)
                        self.boolean_ACK[ACK_num] = True
                        self.frame_buff[cur] = ''  # indicate that the buffer is available in this place

                        # Promote the start to the first package in the window which has not received ACK:
                        while self.boolean_ACK[self.start_window]:
                            self.boolean_ACK[self.start_window] = False
                            self.frame_buff[self.start_window] = ''
                            self.start_window = (self.start_window + 1) % (self.window_size * 2)
                            self.end_window = (self.start_window + self.window_size - 1) % (self.window_size * 2)

                    cur = (self.start_window + 1) % (self.window_size * 2)

        except:
            pass



class Receiver:

    def __init__(self, udp_socket):

        self.soc: socket = udp_socket
        self.buff = 1024
        self.flag = True

        # 1) receives the file details:
        self.data, self.addr = self.soc.recvfrom(self.buff)

        self.soc.sendto('ACK'.encode('utf-8'), self.addr)
        self.file_name, file_size, window_size = self.data.decode('utf-8').split("|||")
        self.file_size = int(file_size)
        self.window_size = int(window_size)
        self.start_window = 0
        self.end_window = self.start_window + self.window_size - 1

        self.frame_num = 0
        self.next_frame = 0
        self.frame_buff = [''] * (self.window_size * 2)
        self.curr_size = 0
        self.boolean_frame = [False] * (self.window_size * 2)

        # 2) open the file:
        self.f = open(self.file_name, 'wb')

        # 3) receive the file:
        self.receive_file()

    # the main func. this func receive the data from the soc and write new file.
    def receive_file(self):

        while self.data:
            try:
                if self.flag:
                    print("window size:", self.window_size)
                    self.data, addr = self.soc.recvfrom(self.buff)
                    self.data = self.data.decode('utf-8')
                    self.write_to_frame(self.data)
                else:
                    return
            except:
                print("Something Went Wrong receive_file")
                self.f.close()
                self.soc.close()
                return

    # help func. this func write the data to the buffer.
    def write_to_frame(self, data):

        print("write_to_frame")
        print(data)
        print("frame:", self.frame_buff)
        print("srart win:", self.start_window)
        if data:
                num = int(data[0])
                data = data[1:]

                cur = self.start_window
                for i in range(self.window_size):
                    if cur == num:
                        print(cur == num)
                        if self.frame_buff[num] == '':
                            self.frame_buff[num] = data

                            # send ACK:
                            ACK = "ACK" + str(num)
                            self.soc.sendto(ACK.encode('utf-8'), self.addr)
                            print("num", num)
                            break

                    cur = (self.start_window + 1) % (self.window_size * 2)

                print(self.start_window)
                if num == self.start_window:
                    self.write_to_file()

    # help func. this func write teh data that in the buffer.
    def write_to_file(self):
        print("write_to_file")
        print("frame:", self.frame_buff)
        for i in range(self.window_size):

                if self.frame_buff[self.start_window] != '':
                    data = self.frame_buff[self.start_window].encode()
                    self.f.write(data)
                    print("write")
                    self.frame_buff[self.start_window] = ''
                    self.start_window = (self.start_window + 1) % (self.window_size * 2)
                    self.end_window = (self.start_window + self.window_size - 1) % (self.window_size * 2)

                    self.curr_size += len(data)
                    rate = round(float(self.curr_size) / float(self.file_size) * 100, 2)
                    print(rate)


                    if self.curr_size >= self.file_size:
                        self.curr_size = self.file_size

                        print("SSSSucceSSSS")
                        self.f.close()
                        self.soc.close()


                        print(f"{self.curr_size}/{self.file_size}, {rate}, %\n")
                        print(data)


                else:
                    break

