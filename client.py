import socket
import threading
import tkinter
import tkinter.scrolledtext
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import simpledialog
# from socket import *
from socket import timeout
import sys
import select
import socket
import os
import sys
import time

HOST = '127.0.0.1'
PORT = 55000

class Client:

    # asks the client his name
    def __init__(self, host, port):

        # connect the client:
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((host, port))

        # starting client with UDP Sscket.
        self.soc_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc_udp.bind(self.soc.getsockname())
        self.soc_udp_addr = self.soc_udp.getsockname()

        window = tk.Tk()
        window.title('Welcome!')
        window.geometry('400x400')
        # canvas = Canvas(window, width=500, height=500)
        # canvas.pack()
        # file = './data/wlecome1.gif'
        # my_image = PhotoImage(file=file)
        # canvas.create_image(0, 0, anchor=NW, imagemy_image)
        # window.mainloop()

        self.name = simpledialog.askstring("Name", "Enter your name:", parent = window)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop) # a thread responsible for running the Gui
        receive_thread = threading.Thread(target=self.receive) # a thread responsible for running the Gui

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):

        #the main window:
        self.win = tk.Tk()
        self.win.title("Messenger")
        self.win.configure(bg = "lightgrey")

        # the main frame:
        self.main_frame = tk.Frame(self.win, relief=tk.RAISED)
        self.main_frame.grid(row=0, column=1, sticky="ns")

        # chat label:
        self.chat_label = tkinter.Label(self.main_frame, text="Chat", bg="lightgrey")
        self.chat_label.config(font=("comicsansms", 12))
        self.chat_label.grid(padx=20, pady=5)

        # the left menu (log out, show online, show server files):
        self.menu_buttons = tk.Frame(self.win, relief=tk.RAISED, bd=3)
        self.out_button = tkinter.Button(self.menu_buttons, text="Log Out", command=self.stop)
        self.online_button = tk.Button(self.menu_buttons, text="Show Online", command=self.show_online)
        self.files_button = tk.Button(self.menu_buttons, text="Show Server Files", command=self.get_files)

        self.out_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.out_button.config(font=("comicsansms", 13))
        self.online_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.online_button.config(font=("comicsansms", 13))
        self.files_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.files_button.config(font=("comicsansms", 13))
        self.menu_buttons.grid(row=0, column=0, sticky="ns")

        # the text area:
        self.text_area = tkinter.scrolledtext.ScrolledText(self.main_frame)
        self.text_area.config(state='disabled')
        self.text_area.grid(padx=20, pady=5)

        # the frame of sending:
        self.message_frame = tk.Frame(self.main_frame, relief=tk.RAISED)
        self.message_frame.grid(padx=20, pady=5)

        # sending messages:
        self.dest_label = tkinter.Label(self.message_frame, text="To (blank to all)", bg="lightgrey")
        self.dest_label.config(font=("comicsansms", 12))
        self.dest_label.grid(row=0, column=0, padx=5, pady=5)
        self.input_dest = tkinter.Text(self.message_frame, height=1, width=15)
        self.input_dest.grid(row=1, column=0, padx=5, pady=5)

        self.msg_label = tkinter.Label(self.message_frame, text="Message", bg="lightgrey")
        self.msg_label.config(font=("comicsansms", 12))
        self.msg_label.grid(row=0, column=1, padx=10, pady=5)
        self.input_area = tkinter.Text(self.message_frame, height=1, width=60)
        self.input_area.grid(row=1, column=1, padx=10, pady=5)

        self.send_button = tkinter.Button(self.message_frame, text="Send", command=self.write)
        self.send_button.config(font=("comicsansms", 12))
        self.send_button.grid(row=1, column=2, padx=5, pady=5)

        # the frame of files:
        self.files_frame = tk.Frame(self.main_frame, relief=tk.RAISED)
        self.files_frame.grid(padx=20, pady=5)

        # files:
        self.src_file_label = tkinter.Label(self.files_frame, text="Server File Name", bg="lightgrey")
        self.src_file_label.config(font=("comicsansms", 12))
        self.src_file_label.grid(row=0, column=0, padx=5, pady=5)
        self.input_src_file = tkinter.Text(self.files_frame, height=1, width=37)
        self.input_src_file.grid(row=1, column=0, padx=5, pady=5)

        self.save_as_label = tkinter.Label(self.files_frame, text="Save As...", bg="lightgrey")
        self.save_as_label.config(font=("comicsansms", 12))
        self.save_as_label.grid(row=0, column=1, padx=10, pady=5)
        self.input_save_file = tkinter.Text(self.files_frame, height=1, width=37)
        self.input_save_file.grid(row=1, column=1, padx=10, pady=5)

        self.proceed_button = tkinter.Button(self.files_frame, text="Download", command=self.download_ask)
        self.proceed_button.config(font=("comicsansms", 12))
        self.proceed_button.grid(row=1, column=2, padx=5, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    # 0) This func sends messages from the client to the other participants in the chat,
    # 1) or to a specific participant.
    def write(self):
        event = '0'
        dest = self.input_dest.get('1.0', 'end').strip()
        print(f"dest: {dest}")
        print(f"len: {len(dest)}")

        if len(dest) > 0:
            event = '1'

        message = f"{event}{dest}{self.name}: {self.input_area.get('1.0', 'end')}"
        print(f"message:{message}")
        self.soc.send(message.encode('utf-8'))
        self.input_dest.delete('1.0', 'end')
        self.input_area.delete('1.0', 'end')

    # 2) The func asks the server to send to the client a list of the online members in the chat.
    def show_online(self):
        self.soc.send("2".encode('utf-8'))


    # 3) The func asks the server to send to the client a list of the server's files.
    def get_files(self):
        self.soc.send("3".encode('utf-8'))

    # 4) The func asks the server to download the desired files.
    def download_ask(self):
        # pass
        print("1")
        file_name = self.input_src_file.get('1.0', 'end').strip()
        save_as = self.input_save_file.get('1.0', 'end').strip()
        msg = f"4{self.soc.getsockname()}:{file_name}:{save_as}"
        self.soc.send(msg.encode('utf-8'))
        download_thread = threading.Thread(target=self.download)
        download_thread.start()
        # self.download()


    # 4 help) The func receives from the server files.
    def download(self):
        BUFF = 1024
        CURR_SIZE = 0  # represents the file size downloaded so far
        ACK = 0
        START_WINDOW = 0

        data, addr = self.soc_udp.recvfrom(BUFF)

        fileName, file_size, window_size = data.decode('utf-8').split("|||")
        window_size = int(window_size)
        END_WINDOW = START_WINDOW + window_size - 1
        WINDOW = [None] * window_size
        FRAME_BUFF = [None] * window_size
        print("Received File : ", fileName)
        f = open(fileName, 'wb') # open the file.

        file_size = int(file_size)

        while CURR_SIZE < file_size:
            print("1")
            index = 0
            for i in range(START_WINDOW, END_WINDOW + 1):
                WINDOW[index] = i
                index += 1

            data, addr = self.soc_udp.recvfrom(BUFF)

            CURR_SIZE += len(data) - 2
            rate = round(float(CURR_SIZE) / float(file_size) * 100, 2)

            if data[len(data) - 1] == str(self.calc_checksum(data)):
                print(f"receive checksum : {data[len(data) - 1]} / calculate checksum : {self.calc_checksum(data)}")
                print("no error")

            if CURR_SIZE > file_size:
                CURR_SIZE = file_size

            print(f"{CURR_SIZE}/{file_size}, {rate}, %\n")
            f.write(data[1:len(data) - 2])
            if CURR_SIZE == file_size:
                print("Success")


            if START_WINDOW is int(data[0]):
                if START_WINDOW is window_size * 2:
                    START_WINDOW %= window_size * 2

                START_WINDOW += 1
                END_WINDOW = START_WINDOW + window_size - 1

            print(WINDOW)

            FRAME_BUFF[WINDOW.index(int(data[0]))] = data
            ACK = "ACK" + data[0]
            self.soc_udp.sendto(ACK, addr)

            if None not in FRAME_BUFF:
                for i in FRAME_BUFF:
                    f.write(i)
                    FRAME_BUFF[FRAME_BUFF.index(i)] = None

        f.close()

    def calc_checksum(self, c_data):
        c_sum = 0

        for i in c_data[1:len(c_data) - 1]:
            c_sum += ord(i)
        c_sum = ~c_sum
        return '%1X' % (c_sum & 0xF)

    def proceed(self):
        pass

    # buf = 1024
    #
    # data, addr = self.soc_udp.recvfrom(buf)
    # file_name = data.decode().strip()
    # print(f"Received File: {file_name}")
    # f = open(data.strip(), 'wb')
    #
    # data, addr = self.soc_udp.recvfrom(buf)
    # try:
    #     while (data):
    #         f.write(data)
    #         self.soc_udp.settimeout(2)
    #         data, addr = self.soc_udp.recvfrom(buf)
    # except timeout:
    #     f.close()
    #     print(f"File {file_name} Downloaded")
    #


    # This func stop the connection with teh server and destroy the Gui screen.
    def stop(self):
        self.running = False
        self.win.destroy()
        self.soc.close()
        self.soc_udp.close()
        exit(0)

    # This func receives messages from server and show the messages on the Gui screen
    def receive(self):
        while self.running:
            try:
                # Receive Message From Server
                message = self.soc.recv(1024).decode('utf-8')
                # If 'NAME' Send the client's name
                if message == 'NAME':
                    self.soc.send(self.name.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.soc.close()
                self.soc_udp.close()
                break

client = Client(HOST, PORT)


