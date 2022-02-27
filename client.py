import socket
import threading
import tkinter
import tkinter.scrolledtext
import tkinter as tk
from tkinter import *
from tkinter import simpledialog


HOST = '127.0.0.1'
PORT = 55000

class Client:

    # ask the client's name for new client
    def __init__(self, host, port):

        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((host, port))

        window = tkinter.Tk()
        window.withdraw()

        self.nickname = simpledialog.askstring("Name", "Enter your name:", parent = window)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

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

        # chat lable:
        self.chat_label = tkinter.Label(self.main_frame, text="Chat", bg="lightgrey")
        self.chat_label.config(font=("comicsansms", 12))
        self.chat_label.grid(padx=20, pady=5)

        # the left menu (log out, show online, show server files):
        self.menu_buttoms = tk.Frame(self.win, relief=tk.RAISED, bd=3)
        self.out_buttom = tkinter.Button(self.menu_buttoms, text="Log Out", command=self.stop)
        self.online_buttom = tk.Button(self.menu_buttoms, text="Show Online", command=self.get_online)
        self.files_buttom = tk.Button(self.menu_buttoms, text="Show Server Files", command=self.get_files)

        self.out_buttom.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.out_buttom.config(font=("comicsansms", 13))
        self.online_buttom.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.online_buttom.config(font=("comicsansms", 13))
        self.files_buttom.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.files_buttom.config(font=("comicsansms", 13))
        self.menu_buttoms.grid(row=0, column=0, sticky="ns")

        # the text area:
        self.text_area = tkinter.scrolledtext.ScrolledText(self.main_frame)
        self.text_area.config(state='disabled')
        self.text_area.grid(padx=20, pady=5)

        # the frame of sending:
        self.messege_frame = tk.Frame(self.main_frame, relief=tk.RAISED)
        self.messege_frame.grid(padx=20, pady=5)

        # sending messages:
        self.dest_label = tkinter.Label(self.messege_frame, text="To (blank to all)", bg="lightgrey")
        self.dest_label.config(font=("comicsansms", 12))
        self.dest_label.grid(row=0, column=0, padx=5, pady=5)
        self.input_dest = tkinter.Text(self.messege_frame, height=1, width=15)
        self.input_dest.grid(row=1, column=0, padx=5, pady=5)

        self.msg_label = tkinter.Label(self.messege_frame, text="Message", bg="lightgrey")
        self.msg_label.config(font=("comicsansms", 12))
        self.msg_label.grid(row=0, column=1, padx=10, pady=5)
        self.input_area = tkinter.Text(self.messege_frame, height=1, width=60)
        self.input_area.grid(row=1, column=1, padx=10, pady=5)

        self.send_buttom = tkinter.Button(self.messege_frame, text="Send", command=self.write)
        self.send_buttom.config(font=("comicsansms", 12))
        self.send_buttom.grid(row=1, column=2, padx=5, pady=5)

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

        self.proceed_buttom = tkinter.Button(self.files_frame, text="proceed", command=self.proceed)
        self.proceed_buttom.config(font=("comicsansms", 12))
        self.proceed_buttom.grid(row=1, column=2, padx=5, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def get_online(self):
        pass

    def proceed(self):
        pass

    def get_files(self):
        pass

    def stop(self):
        self.running = False
        self.win.destroy()
        self.soc.close()
        exit(0)

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.soc.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def receive(self):
        while self.running:
            try:
                # Receive Message From Server
                # If 'NICK' Send Nickname
                message = self.soc.recv(1024).decode('utf-8')
                if message == 'NAME':
                    self.soc.send(self.nickname.encode('utf-8'))
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
                break
client = Client(HOST, PORT)


