from socket import *
import time
import argparse


def client_ping(count,serverAddress,serverPort,timeOut):
    print('pinging',serverAddress)
    clientSocket = socket(AF_INET,SOCK_DGRAM)
    clientSocket.settimeout(timeOut)

    message = "ping"
    message = message.encode()

    avrg = 0
    diff = 0

    for _ in range(count):
        try:
            start = time.perf_counter()
            clientSocket.sendto(message,(serverAddress,serverPort))
            responseMessage = clientSocket.recvfrom(2048)

            if responseMessage:
                end = time.perf_counter()
                rtt = (end - start) * 1000
                print("reply from",serverAddress,"in",rtt,"ms")

            avrg = avrg + rtt
        except timeout:
            print("ping failed timeout")
        except ConnectionResetError :
            print("ping failed server unreachable")
    print("the average RTT is",avrg/count)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PING to a server"
    )

    parser.add_argument("--serverAddress",default="127.0.0.1")
    parser.add_argument("--serverPort",default=1234,type=int)
    parser.add_argument("--count",default=4,type=int)
    parser.add_argument("--timeOut",default=1.0,type=float)
    args = parser.parse_args()

    serverAddress = args.serverAddress
    serverPort = args.serverPort
    count = args.count
    timeOut = args.timeOut

    client_ping(count,serverAddress,serverPort,timeOut)