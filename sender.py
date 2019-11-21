import socket
import time

ack = 2

if __name__ == "__main__":
    RECEIVER_IP = ""
    RECEIVER_PORT = 5005
    MYIP = ""
    MY_PORT = 5006
    print(MYIP)
    fileName = "IMG_20180425_103211.jpg"
    file = open(fileName, "rb")
    file.seek(0, 2)
    fileLength = file.tell()
    file.seek(0, 0)
    sizeOfFrame = 100
    nrOfPackets = int(fileLength / sizeOfFrame)
    print("Numarul de pachete:", nrOfPackets)
    header = 8
    firstFrame = b''
    firstFrame += header.to_bytes(1, "big")
    firstFrame += nrOfPackets.to_bytes(4, "big")
    firstFrame += fileName.encode("UTF-8")
    print("Fisierul are dimensiunea de %d octeti" %(fileLength))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(firstFrame, (RECEIVER_IP, RECEIVER_PORT))
    packetID = 1
    isReading = True
    header = 4
    while isReading:
        dataToSend = file.read(sizeOfFrame)
        if file.tell() == fileLength:
            isReading = False
        dataLength = len(dataToSend)
        dataToSend = header.to_bytes(1, "big") + packetID.to_bytes(4, "big") + dataLength.to_bytes(4, "big") + dataToSend
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(dataToSend, (RECEIVER_IP, RECEIVER_PORT))
        packetID += 1
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock2.bind((MYIP, MY_PORT))
        if packetID % 200 == 0:
            time.sleep(1)
        receivedData, addr = sock2.recvfrom(1024)
        print(receivedData.hex())
        if receivedData[0] == ack:
            print('Am primit ACK pentru: ', receivedData[1:5].hex())
    file.close()
