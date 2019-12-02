
import socket
from random import random


class Reciver:
    def __init__(self, ip, port):
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.Nack = 1
        self.Ack = 2
        self.Data =4
        self.INF = 8

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
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, UDP_PORT))
            print(UDP_IP)
            numberOfPackets = 0
            fileName = ""
            packetID = 0
            length = 0
            packetExpected = 1
            file = 0
            while True:
                data, addr = sock.recvfrom(1024)
                packet=bytes(data)
                print(addr)
                if packet[0] == self.INF:
                    print("Pachet tip informatie inceput")
                    numberOfPackets, fileName = self.decodeINF(packet)
                    print(numberOfPackets, " pachete")
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
                        if a>0.03:
                            s = sock2.sendto(toSend, (addr[0], 5006))
                            packetExpected += 1
                            if packetID==numberOfPackets:
                                print(length)
                                file.write(packet[9:length+1])
                                break
                            else:
                                file.write(packet[9:])
                        else:
                            print("N-am primit")

            sock.close()
            sock2.close()
            file.close()
        except:
            print("A error");




if __name__ == "__main__":
    UDP_IP = socket.gethostbyname(socket.gethostname())
    UDP_PORT = 5005
    reciver = Reciver(UDP_IP, UDP_PORT)
    reciver.start()