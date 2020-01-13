import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import socket
from threading import Thread
import subprocess
import time

FRAME_INFORMATION = 8
FRAME_DATA = 4
FRAME_ACKNOWLEDGE = 2


class Thread2(Thread):
    def __init__(self, apl, s):
        Thread.__init__(self)
        self.apl = apl
        self.s = s

    def run(self):
        if self.apl and self.s:
            while True:
                if self.s.nrOfPackets:
                    self.apl.progressBar['value'] = self.s.nrOfPacketsConf*100/self.s.nrOfPackets
                    if self.s.nrOfPacketsConf == self.s.nrOfPackets:
                        break
                if not self.apl.thread1.is_alive():
                    exit(-1)


class Sender:
    def __init__(self, fileName, RECV_IP, RECV_PORT, MY_IP, MY_PORT, windowSize, timeout):
        self.MY_IP = MY_IP
        self.MY_PORT = MY_PORT
        self.RECEIVER_IP = RECV_IP
        self.RECEIVER_PORT = RECV_PORT
        self.sizeOfFrame = 1500
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.MY_IP, self.MY_PORT))
        self.fileName = fileName
        self.nrOfPackets = 0
        self.nrOfPacketsConf = 0
        self.windowSize = windowSize
        self.timeout = timeout
        self.log = open('log.txt', 'w')

    def writeLog(self, message):
        header = time.strftime('%d-%m-%Y %H:%M:%S') + ': '
        self.log.write(header + message + '\n')

    def readFile(self):
        self.file = open(self.fileName, "rb")
        self.file.seek(0, 2)
        self.fileLength = self.file.tell()
        self.file.seek(0, 0)
        self.nrOfPackets = int(self.fileLength / self.sizeOfFrame)
        if self.fileLength % self.sizeOfFrame:
            self.nrOfPackets += 1

    def sendInfo(self):
        header = FRAME_INFORMATION
        firstFrame = b''
        firstFrame += header.to_bytes(1, "big")
        firstFrame += self.nrOfPackets.to_bytes(4, "big")
        firstFrame += self.MY_PORT.to_bytes(2, "big")
        firstFrame += self.fileName[self.fileName.rfind("/")+1:].encode("UTF-8")
        self.sock.sendto(firstFrame, (self.RECEIVER_IP, self.RECEIVER_PORT))
        self.writeLog('S-a trimis pachetul de informatii. Datele fisierului:')
        self.writeLog('Nume fisier: ' + self.fileName[self.fileName.rfind("/")+1:])
        self.writeLog('Numar de pachete: ' + str(self.nrOfPackets))

    def sendData(self):
        global nRead
        global packetsLeftToSend
        global packetsLeftToReceive
        packetID = 1
        header = FRAME_DATA
        nRead = self.windowSize
        attemptsToSend = 0
        packetsLeftToSend = True
        packetsLeftToReceive = True
        while packetsLeftToReceive or packetsLeftToSend:
            if packetsLeftToSend:
                for i in range(nRead):
                    dataToSend = self.file.read(self.sizeOfFrame)
                    dataLength = len(dataToSend)
                    dataToSend = header.to_bytes(1, "big") + packetID.to_bytes(4, "big") + dataLength.to_bytes(4, "big") + dataToSend
                    self.sock.sendto(dataToSend, (self.RECEIVER_IP, self.RECEIVER_PORT))
                    self.writeLog('S-a trimis pechetul cu numarul ' + str(packetID))
                    packetID += 1
            if packetsLeftToReceive:
                self.sock.settimeout(self.timeout)
                try:
                    receivedData, addr = self.sock.recvfrom(1024)
                    if receivedData[0] == FRAME_ACKNOWLEDGE:
                        nr = int.from_bytes(receivedData[1:5], 'big')
                        self.writeLog('S-a receptionat ACK pentru pachetul ' + str(nr))
                        self.nrOfPacketsConf += 1
                        if receivedData[1:5] == (packetID-self.windowSize).to_bytes(4, 'big'):
                            nRead = 1
                        else:
                            self.file.seek(-self.windowSize*self.sizeOfFrame, 1)
                            packetID -= self.windowSize
                            nRead = self.windowSize
                except:
                    attemptsToSend += 1
                    if attemptsToSend == 10:
                        self.writeLog('S-a depasit numarul maxim de trimiteri. Nu poate realiza transferul')
                        self.closeTransfer()
                        quit(-1)
                    self.file.seek(-self.windowSize*self.sizeOfFrame, 1)
                    packetID -= self.windowSize
                    packetsLeftToSend = True
                    packetsLeftToReceive = True
                    nRead = self.windowSize
            if packetID - 1 == self.nrOfPackets:
                packetsLeftToSend = False
            if self.nrOfPacketsConf == self.nrOfPackets:
                packetsLeftToReceive = False
        self.closeTransfer()

    def closeTransfer(self):
        self.file.close()
        self.log.close()
        self.sock.close()

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.linkVarIP = tk.StringVar()
        self.linkVarPORT = tk.StringVar()
        self.linkVarReceiverIP = tk.StringVar()
        self.linkVarReceiverPORT = tk.StringVar()
        self.linkVarFileName = tk.StringVar()
        self.linkVarWindowSize = tk.StringVar()
        self.linkVarTimeout = tk.StringVar()
        self.ReceiverIP = ''
        self.ReceiverPORT = 0
        self.fileName = ''
        self.listOfIP = []
        self.getIPs()
        self.thread1 = ''
        self.thread2 = ''
        self.isConfigured = False
        self.create_interface()

    def getIPs(self):
        data = str(subprocess.check_output('ipconfig'), 'UTF-8')
        listOfData = data.splitlines()
        for line in listOfData:
            if line.find('IPv4 Address') != -1:
                idx = line.find(':')
                self.listOfIP.append(line[idx+2:])

    def create_interface(self):
        self.labelMyIP = tk.Label(self, text='IP : ')
        self.labelMyIP.grid(row=0, column=0, pady=15)
        self.inMyIP = ttk.Combobox(self, textvariable=self.linkVarIP)
        self.inMyIP['values'] = self.listOfIP
        self.inMyIP.grid(row=0, column=1, pady=15)

        self.labelMyPORT = tk.Label(self, text='PORT: ')
        self.labelMyPORT.grid(row=1, column=0, pady=5)
        self.inMyPORT = tk.Entry(self, textvariable=self.linkVarPORT)
        self.linkVarPORT.set('5006')
        self.inMyPORT.grid(row=1, column=1, pady=5)

        self.labelReceiverIP = tk.Label(self, text='IP receptor: ')
        self.labelReceiverIP.grid(row=0, column=2, pady=15)
        self.inReceiverIP = tk.Entry(self, textvariable=self.linkVarReceiverIP)
        self.inReceiverIP.grid(row=0, column=3, pady=15)

        self.labelReceiverPORT = tk.Label(self, text='PORT receptor: ')
        self.labelReceiverPORT.grid(row=1, column=2, pady=5)
        self.inReceiverPORT = tk.Entry(self, textvariable=self.linkVarReceiverPORT)
        self.inReceiverPORT.grid(row=1, column=3, pady=5)
        self.linkVarReceiverPORT.set('5005')

        self.button = tk.Button(self, text='Configurare', command=self.validateInput)
        self.button.grid(row=2, column=0, columnspan=2, pady=5)

        self.labelInfoConfig = tk.Label(self, text='STATUS: neconfigurat')
        self.labelInfoConfig.grid(row=2, column=2, columnspan=2, pady=5)

        self.labelFileName = tk.Label(self, text='Fisierul nu a fost incarcat')
        self.labelFileName.grid(row=3, column=0, columnspan=4, pady=5)

        self.buttonOpenFile = tk.Button(self, text='Deschidere fisier', command=self.selectFile)
        self.buttonOpenFile.grid(row=4, column=0, columnspan=4, pady=5)

        self.buttonSend = tk.Button(self, text="Trimite", command=self.createSendThread)
        self.buttonSend.grid(row=5, column=0, columnspan=4, pady=5)

        self.progressBar = ttk.Progressbar(self, length='450')
        self.progressBar['maximum'] = 100
        self.progressBar.grid(row=6, column=0, columnspan=4, pady=5)

        self.labelWindowSize = tk.Label(self, text='Dimensiunea ferestrei: ')
        self.labelWindowSize.grid(row=7, column=0, pady=5)

        self.inWindowSize=tk.Entry(self, textvariable=self.linkVarWindowSize)
        self.inWindowSize.grid(row=7, column=1, columnspan=2)
        self.linkVarWindowSize.set('5')

        self.labelWindowSize = tk.Label(self, text='Timeout pentru receptie (secs): ')
        self.labelWindowSize.grid(row=7, column=2, pady=5)

        self.inTimeout=tk.Entry(self, textvariable=self.linkVarTimeout)
        self.inTimeout.grid(row=7, column=3, pady=5)
        self.linkVarTimeout.set('0.5')

    def validateInput(self):
        nr = 0
        if self.validateIP(self.linkVarReceiverIP.get()):
            self.ReceiverIP = self.linkVarReceiverIP.get()
            nr += 1
        else:
            print('IP  receptor invalid')
        if self.validatePORT(self.linkVarReceiverPORT.get()):
            self.ReceiverPORT = self.linkVarReceiverPORT.get()
            nr += 1
        else:
            print('PORT receptor invalid')
        if self.validateIP(self.linkVarIP.get()):
            self.MyIP = self.linkVarIP.get()
            nr += 1
        else:
            print('IP invalid')
        if self.validatePORT(self.linkVarPORT.get()):
            self.MyPORT = self.linkVarPORT.get()
            nr += 1
        else:
            print('PORT invalid')
        if nr == 4:
            self.labelInfoConfig['text'] = 'STATUS: configurat'
            self.isConfigured = True
        else:
            self.labelInfoConfig['text'] = 'STATUS: neconfigurat'

    def validatePORT(self, PORT):
        ok = True
        if not PORT.isdigit():
            ok = False
        if ok:
            if int(PORT) < 0 or int(PORT) > 65535:
                ok = False
            if ok:
                return True
            else:
                return False
        else:
            return False

    def validateIP(self, IP):
        ok = True
        for i in range(len(IP)):
            if IP[i] not in '0123456789.':
                ok = False
        if ok:
            if IP.count('.') != 3:
                ok = False
            if ok:
                list = IP.split('.')
                for nr in list:
                    if int(nr) < 0 or int(nr) > 255:
                        ok = False
                if ok:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def createSendThread(self):
        if self.isConfigured and self.fileName:
            self.buttonSend["state"] = "disabled"
            self.thread1 = Thread(target=self.sendFile, args=())
            self.thread1.start()
        else:
            print("aplicatia nu este configurata")

    def selectFile(self):
        self.fileName = filedialog.askopenfilename()
        self.labelFileName['text'] = 'Fisierul selectat pentru transfer: ' + self.fileName
        self.progressBar['value'] = 0
        self.buttonSend["state"] = "active"

    def sendFile(self):
        windowSize = int(self.linkVarWindowSize.get())
        timeout = float(self.linkVarTimeout.get())
        s = Sender(self.fileName, self.ReceiverIP, int(self.ReceiverPORT), self.MyIP, int(self.MyPORT), windowSize, timeout)
        self.thread2 = Thread2(self, s)
        self.thread2.start()
        s.readFile()
        s.sendInfo()
        s.sendData()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('600x320+100+75')
    root.title('Transfer de fisiere')
    app = Application(master=root)
    app.mainloop()
