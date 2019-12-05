import socket

FRAME_INFO = 8
FRAME_DATA = 4
FRAME_ACKNOWLEDGE = 2


class Sender:
    def __init__(self, IP, PORT, MY_IP, MY_PORT):
        self.IP = IP
        self.PORT = PORT
        self.MY_IP = MY_IP
        self.MY_PORT = MY_PORT
        self.sizeOfFrame = 1500
        self.sock_transmit = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv.bind((self.MY_IP, self.MY_PORT))

    def readFile(self, fileName):
        self.fileName = fileName
        self.file = open(self.fileName, "rb")
        self.file.seek(0, 2)
        self.fileLength = self.file.tell()
        self.file.seek(0, 0)
        self.nrOfPackets = int(self.fileLength / self.sizeOfFrame)

    def sendInfo(self):
        header = FRAME_INFO
        firstFrame = b''
        firstFrame += header.to_bytes(1, "big")
        firstFrame += self.nrOfPackets.to_bytes(4, "big")
        firstFrame += fileName.encode("UTF-8")
        self.sock_transmit.sendto(firstFrame, (RECEIVER_IP, RECEIVER_PORT))


    def sendData(self):
        global nRead
        packetID = 1
        header = FRAME_DATA
        windowSize = 5
        nRead = windowSize
        while packetID <= self.nrOfPackets:
            for i in range(nRead):
                dataToSend = self.file.read(self.sizeOfFrame)
                dataLength = len(dataToSend)
                dataToSend = header.to_bytes(1, "big") + packetID.to_bytes(4, "big") + dataLength.to_bytes(4, "big") + dataToSend
                self.sock_transmit.sendto(dataToSend, (self.IP, self.PORT))
                print('Am trimis pechetul ', packetID)
                packetID += 1
            self.sock_recv.settimeout(0.5)
            try:
                receivedData, addr = self.sock_recv.recvfrom(1024)
                if receivedData[0] == FRAME_ACKNOWLEDGE:
                    print('Am primit ACK pentru: ', receivedData[1:5].hex())
                    if receivedData[1:5] == (packetID-windowSize).to_bytes(4,'big'):
                        nRead = 1
                    else:
                        print(receivedData[1:5].hex())
                        self.file.seek(-windowSize*self.sizeOfFrame, 1)
                        packetID -= windowSize
                        nRead = windowSize
                        print(packetID)
            except:
                self.file.seek(-windowSize*self.sizeOfFrame, 1)
                packetID -= windowSize
                nRead = windowSize
        for i in range(windowSize - 1):
            try:
                receivedData, addr = self.sock_recv.recvfrom(1024)
                if receivedData[0] == FRAME_ACKNOWLEDGE:
                    print('Am primit ACK pentru: ', receivedData[1:5].hex())
                    if receivedData[1:5] == (packetID-windowSize).to_bytes(4, 'big'):
                        nRead = 1
                    else:
                        print(receivedData[1:5].hex())
                        self.file.seek(-windowSize*self.sizeOfFrame, 1)
                        packetID -= windowSize
                        nRead = windowSize
            except:
                self.file.seek(-windowSize*self.sizeOfFrame, 1)
                packetID -= windowSize
                nRead = windowSize
        self.file.close()


if __name__ == "__main__":
    MY_IP = ""
    MY_PORT = 5006
    RECEIVER_IP = ""
    RECEIVER_PORT = 5005
    fileName = "IMG_20180425_103211_2.jpg"
    s = Sender(RECEIVER_IP, RECEIVER_PORT, MY_IP, MY_PORT)
    s.readFile(fileName)
    s.sendInfo()
    s.sendData()
