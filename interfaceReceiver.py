import tkinter as tk
from tkinter.ttk import *
import socket

class App(tk.Frame):
     def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.labelIP = tk.Label(parent, text="Your IP: ")
        self.labelIP.grid(row=0, column=0, pady=2)
        self.entryIP = tk.Entry(parent)
        self.entryIP.grid(row=0,column=1, pady=4)
        self.entryIP.insert(0,socket.gethostbyname(socket.gethostname()))
        self.labelPort = tk.Label(parent, text="Port: ")
        self.labelPort.grid(row=1, column=0, pady=2)
        self.entryPort = tk.Entry(parent)
        self.entryPort.grid(row=1, column=1, pady=4)
        self.labelInfo = tk.Label(parent, text="Press 'Start' to wait packets")
        self.labelInfo.grid(row=2, column=0, columnspan=3)
        self.button = tk.Button(parent, text="Start")
        self.button.grid(row=2,column=4, sticky=tk.E)
        self.labelProgress = tk.Label(parent, text="Progress:")
        self.labelProgress.grid(row=4, column=0)
        self.progressbar = Progressbar(parent, orient = tk.HORIZONTAL, length = 100, mode = 'determinate')
        self.progressbar.grid(row=4, column=1, sticky=tk.NE)


class AppInfo(tk.Frame):
    def __init__(self,parent, message):
        tk.Frame.__init__(self, parent)
        self.labelInfo = tk.Label(parent, text=message)
        self.labelInfo.grid(row=0, column=0, columnspan=3)
        self.exitButton = tk.Button(parent, text="Ok", command=parent.quit)
        self.exitButton.grid(row=1, column=1)
