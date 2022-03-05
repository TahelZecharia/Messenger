import socket
import threading
import tkinter
import tkinter.scrolledtext
import tkinter as tk
from tkinter import simpledialog
from RDT import Receiver

HOST = '127.0.0.1'
PORT = 55000

class Client:

    # asks the client his name
    def __init__(self, host, port):

        # connect the client:
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((host, port))

        # starting client with UDP Sscket:
        self.soc_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc_udp.bind(self.soc.getsockname())
        self.soc_udp_addr = self.soc_udp.getsockname()

        # starting simpledialog:
        window = tk.Tk()
        window.title('Welcome!')
        window.withdraw()

        self.name = simpledialog.askstring("Name", "Enter your name:", parent = window)
        print(self.name)

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
        self.main_frame = tk.Frame(self.win, relief=tk.RAISED, bg="lavenderblush")
        self.main_frame.grid(row=0, column=1, sticky="ns")

        # chat label:
        self.chat_label = tkinter.Label(self.main_frame, text="Chat", bg="lavenderblush")
        self.chat_label.config(font=("Comic Sans MS", 20, "bold"))
        self.chat_label.grid(padx=20, pady=2)

        # name label:
        text = f"Your Name: {self.name}"
        self.name_label = tkinter.Label(self.main_frame, text=text, bg="lavenderblush")
        self.name_label.config(font=("Comic Sans MS", 16, "bold"))
        self.name_label.grid(padx=20, pady=2)

        # the left menu (log out, show online, show server files):
        self.menu_buttons = tk.Frame(self.win, relief=tk.RAISED, bd=3, bg="lavenderblush")
        self.out_button = tk.Button(self.menu_buttons, text="Log\nOut", command=self.stop, bg="lightcoral")
        self.files_button = tk.Button(self.menu_buttons, text="Show\nServer\nFiles", command=self.get_files,bg="lightcoral")
        self.online_button = tk.Button(self.menu_buttons, text="Show\n Onlines", command=self.show_online, bg="lightcoral")


        self.out_button.grid(row=0, column=0, sticky="ew", padx=5, pady=15)
        self.out_button.config(font=("Comic Sans MS", 13, "bold"))
        self.files_button.grid(row=1, column=0, sticky="ew", padx=5, pady=15)
        self.files_button.config(font=("Comic Sans MS", 13, "bold"))
        self.online_button.grid(row=2, column=0, sticky="ew", padx=5, pady=15)
        self.online_button.config(font=("Comic Sans MS", 13, "bold"))
        self.menu_buttons.grid(row=0, column=0, sticky="ns")

        # the text area:
        self.text_area = tkinter.scrolledtext.ScrolledText(self.main_frame, width=55, height=22)
        self.text_area.config(state='disabled')
        self.text_area.grid(padx=15, pady=5)

        # the frame of sending:
        self.message_frame = tk.Frame(self.main_frame, relief=tk.RAISED, bg="lavenderblush")
        self.message_frame.grid(padx=20, pady=5)

        # sending messages:
        self.dest_label = tkinter.Label(self.message_frame, text="To (blank to all)", bg="lavenderblush")
        self.dest_label.config(font=("Comic Sans MS", 12, "bold"))
        self.dest_label.grid(row=0, column=0, padx=5, pady=1)
        self.input_dest = tkinter.Text(self.message_frame, height=1, width=10)
        self.input_dest.grid(row=1, column=0, padx=5, pady=1)

        self.msg_label = tkinter.Label(self.message_frame, text="Message", bg="lavenderblush")
        self.msg_label.config(font=("Comic Sans MS", 12, "bold"))
        self.msg_label.grid(row=0, column=1, padx=10, pady=1)
        self.input_area = tkinter.Text(self.message_frame, height=1, width=30)
        self.input_area.grid(row=1, column=1, padx=10, pady=1)

        self.send_button = tkinter.Button(self.message_frame, text="Send", command=self.write, bg="lightcoral")
        self.send_button.config(font=("Comic Sans MS", 12, "bold"))
        self.send_button.grid(row=1, column=2, padx=5, pady=1)

        # the frame of files:
        self.files_frame = tk.Frame(self.main_frame, relief=tk.RAISED, bg="lavenderblush")
        self.files_frame.grid(padx=20, pady=1)

        # files:
        self.src_file_label = tkinter.Label(self.files_frame, text="Server File Name", bg="lavenderblush")
        self.src_file_label.config(font=("Comic Sans MS", 12, "bold"))
        self.src_file_label.grid(row=0, column=0, padx=5, pady=1)
        self.input_src_file = tkinter.Text(self.files_frame, height=1, width=20)
        self.input_src_file.grid(row=1, column=0, padx=5, pady=1)

        self.save_as_label = tkinter.Label(self.files_frame, text="Save As...", bg="lavenderblush")
        self.save_as_label.config(font=("Comic Sans MS", 12, "bold"))
        self.save_as_label.grid(row=0, column=1, padx=10, pady=1)
        self.input_save_file = tkinter.Text(self.files_frame, height=1, width=20)
        self.input_save_file.grid(row=1, column=1, padx=10, pady=1)

        self.proceed_button = tkinter.Button(self.files_frame, text="Download", command=self.download_ask, bg="lightcoral")
        self.proceed_button.config(font=("Comic Sans MS", 12, "bold"))
        self.proceed_button.grid(row=1, column=2, padx=5, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    # 0) This func sends messages from the client to the other participants in the chat,
    # 1) or to a specific participant.
    def write(self):
        event = '0'
        dest = self.input_dest.get('1.0', 'end').strip()
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
        self.input_src_file.delete('1.0', 'end')
        self.input_save_file.delete('1.0', 'end')
        download_thread = threading.Thread(target=self.download)
        download_thread.start()

    # 4 help) The func receives from the server files.
    def download(self):
        Receiver(self.soc_udp)

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
                        self.text_area.insert('end', '\n')
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


