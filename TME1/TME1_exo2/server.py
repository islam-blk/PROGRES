from socket import *
import time
import argparse
from threading import *
def handle_client(connectionSocket,clientAddress):
        print("handling client",clientAddress)
        try:
            while True:    
                message = connectionSocket.recv(2048).decode()
                if not message:
                    break
                serverTime = str(time.time()).encode()
                connectionSocket.send(serverTime)
        except ConnectionError:
            print("lost connection",clientAddress)
        finally:
            connectionSocket.close()
            print("client disconnected", clientAddress)


def run_server(serverPort):
    serverSocket = socket(AF_INET,SOCK_STREAM)

    try:
        serverSocket.bind(('',serverPort))
        serverSocket.listen(5)
        print("server ready")
        while True:
            connectionSocket,clientAddress = serverSocket.accept()
            Thread(target=handle_client,
           args=(connectionSocket,clientAddress),daemon=True).start()
    except KeyboardInterrupt:
        print("server stoped")
    finally:
        serverSocket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                description="offset "
            )
    parser.add_argument("--serverPort", type=int, default=2345, help="server port")
    args = parser.parse_args()
    serverPort = args.serverPort

    run_server(serverPort)

