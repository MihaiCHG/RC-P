
from random import random
from interfaceReceiver import *
import threading
import sys
sys.path.append('..//')


class Receiver:
    def __init__(self, ip, port, app):
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.Nack = 1
        self.Ack = 2
        self.Data = 4
        self.INF = 8
        self.interface = app
        self.message = ""

    def decodeData(self, packet):
        pID = packet[1:5]
        len = packet[5:9]
        data = packet[9:]
        return pID, len, data

    def decodeINF(self, packet):
        packets = packet[1:5]
        fname = packet[5:]
        return packets, fname

    def encodeAck(self, pID):
        toSend = b''
        toSend = toSend + self.Ack.to_bytes(1, "big") + pID
        return toSend

    def start(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.UDP_IP, self.UDP_PORT))
            print(self.UDP_IP)
            numberOfPackets = 0
            fileName = ""
            packetID = 0
            length = 0
            packetExpected = 1
            file = 0
            while True:
                data, addr = sock.recvfrom(2048)
                packet=bytes(data)
                print(addr)
                if packet[0] == self.INF:
                    print("Pachet tip informatie inceput")
                    numberOfPackets, fileName = self.decodeINF(packet)
                    print(int.from_bytes(numberOfPackets,"big"), " pachete")
                    print("Nume fisier ", fileName, ", numar de pachete ", numberOfPackets.hex())
                    file = open(fileName, "wb")
                if packet[0] == self.Data:
                    print("Pachet tip date")
                    packetID, length, dataF = self.decodeData(packet)
                    print(packetID)
                    if packetExpected.to_bytes(4, "big") == packetID:
                        print("Numar de secventa ", packetID.hex(), ", lungime ", length.hex())
                        toSend = self.encodeAck(packetID)
                        a = random()
                        if a > 0.003:
                            s = sock.sendto(toSend, (addr[0], 5006))
                            packetExpected += 1
                            file.write(packet[9:])
                            percent = int(int.from_bytes(packetID,"big")*100. / int.from_bytes(numberOfPackets,"big"))
                            self.interface.progressbar.config(value=percent)
                            if packetID == numberOfPackets:
                                break
                        else:
                            print("N-am primit")

            sock.close()
            file.close()
            self.interface.button.config(state="normal")
            self.interface.progressbar.config(value=0)
            self.message = "Transfer completed!!!"
        except:
            print("A error")
            self.message = "Transfer failed!!!"
        finally:
            win = tk.Tk()
            appMsg = AppInfo(win, self.message)
            appMsg.mainloop()


def initialize(app):
    UDP_IP =app.entryIP.get()
    UDP_PORT = int(app.entryPort.get())
    app.button.config(state = "disabled")
    receiver = Receiver(UDP_IP, UDP_PORT,app)
    thread = threading.Thread(target=receiver.start, args=())
    thread.start()


def main():
    root = tk.Tk()
    root.geometry("250x120")
    app = App(root)
    app.button.configure(command=lambda: initialize(app))
    app.mainloop()


if __name__ == "__main__":
    main()
