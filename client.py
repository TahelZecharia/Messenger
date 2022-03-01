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
        self.soc_udp_addr =  self.soc_udp.getsockname()

        window = tkinter.Tk()
        window.withdraw()

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

        buf = 1024

        data, addr = self.soc_udp.recvfrom(buf)
        file_name = data.decode().strip()
        print(f"Received File: {file_name}")
        f = open(data.strip(), 'wb')

        data, addr = self.soc_udp.recvfrom(buf)
        try:
            while (data):
                f.write(data)
                self.soc_udp.settimeout(2)
                data, addr = self.soc_udp.recvfrom(buf)
        except timeout:
            f.close()
            print(f"File {file_name} Downloaded")

    def proceed(self):
        pass

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


