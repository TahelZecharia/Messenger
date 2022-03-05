import unittest
import server
from client import Client
from RDT import Sender
from RDT import Receiver
import time

HOST = '127.0.0.1'
PORT = 55000

class Test(unittest.TestCase):

    Eitan = Client(HOST, PORT)
    Tahel = Client(HOST, PORT)

    Eitan.soc.send("Eitan".encode('utf-8'))
    Tahel.soc.send("Tahel".encode('utf-8'))

    def test_name(self):

        self.assertEqual("Eitan", self.Eitan.name)
        self.assertEqual("Tahel", self.Tahel.name)

    def test_online_list(self):

        online = self.Eitan.soc.send("2".encode('utf-8'))

        time.sleep(2)

        names = ["Eitan", "Tahel"]
        msg = "The Online Members Are:\n"
        for name in names:
            msg = msg + "         " + str(name) + "\n"

        self.assertEqual(msg, online)

    def test_files_list(self):

        files = ["file1", "file2", "file3"]

        ans = self.Tahel.soc.send("3".encode('utf-8'))

        time.sleep(2)

        msg = "The Server Files Are:\n"
        for file in files:
            msg = msg + "     " + file + "\n"

        self.assertEqual(ans, msg)