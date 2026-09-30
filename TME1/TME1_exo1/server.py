from socket import *
import random
import argparse


def server_ping(serverPort,missRate):
    serverSocket = socket(AF_INET,SOCK_DGRAM)
    serverSocket.bind(('',serverPort))
    print("server ready")
    responseMessage = "pong"
    responseMessage = responseMessage.encode()

    while True:
        message, clientAddress = serverSocket.recvfrom(2048)

        if random.random() >missRate:
            print("pinged from", clientAddress)
            serverSocket.sendto(responseMessage,clientAddress)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="PING server"
        )
    parser.add_argument("--serverPort", type=int, default=1234, help="server port")
    parser.add_argument("--missRate", type=float, default=0.5, help="miss rate")
    args = parser.parse_args()
    serverPort = args.serverPort
    missRate = args.missRate
    server_ping(serverPort,missRate)
