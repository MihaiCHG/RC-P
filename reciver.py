import socket
Nack = 1
Ack = 2
Data = 4
INF = 8

try:
    UDP_IP = socket.gethostbyname(socket.gethostname())
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(UDP_IP)
    nr_pachete = 0
    numeFis = ""
    numarPachet = 0
    lungime = 0
    packetAsteptat = 1
    file = 0
    while True:
        data, addr = sock.recvfrom(1024)
        packet=bytes(data)
        print(addr)
        if packet[0] == INF:
            print("Pachet tip informatie inceput")
            nr_pachete = packet[1:5]
            print(nr_pachete)
            numeFis = packet[5:]
            print("Nume fisier ", numeFis, ", numar de pachete ", nr_pachete.hex())
            file = open(numeFis,"wb")
        if packet[0] == Data:
            print("Pachet tip date")
            numarPachet = packet[1:5]
            if packetAsteptat.to_bytes(4, "big") == numarPachet:
                lungime = packet[5:9]
                print("Numar de secventa ", numarPachet.hex(), ", lungime ", lungime.hex())
                toSend = b''
                toSend = toSend + Ack.to_bytes(1, "big") + numarPachet
                print(toSend.hex())
                s= sock2.sendto(toSend, (addr[0], 5006))

                #print(s)
                print("adasd")
                packetAsteptat += 1
                if numarPachet==nr_pachete:
                    print(lungime)
                    file.write(packet[9:lungime+1])
                    break
                else:
                    file.write(packet[9:])


    sock.close()
    sock2.close()
    file.close()
except:
    print()
