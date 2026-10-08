from socket import *
from threading import *
import argparse

def forward(src,dest):
    
    while True:
        message = src.recv(2048)
        if message == b'':
            break
        dest.sendall(message)
    dest.shutdown(SHUT_WR)
   

def client_handler(clientRelayConnectionSocket:socket,clientAddress,serverAddress,serverPort):
    try:
        print("handling client",clientAddress)
        relayServerSocket = socket(AF_INET,SOCK_STREAM)
        relayServerSocket.connect((serverAddress,serverPort))
        t = Thread(target=forward,
                args=(relayServerSocket,clientRelayConnectionSocket))
        t.start()
        forward(clientRelayConnectionSocket,relayServerSocket)
        t.join()

    except ConnectionRefusedError:
        print("server not running")
    except gaierror:
            print("can't resolve address")
    except ConnectionError:
            print("connection lost")
    finally:
         relayServerSocket.close()
         clientRelayConnectionSocket.close()


def run_relay(relayPort,serverAddress,serverPort):
    try:
        clientRelaySocket = socket(AF_INET,SOCK_STREAM)

        clientRelaySocket.bind(('',relayPort))
        clientRelaySocket.listen(5)
        print('Relay ready!!!')
        
        while True:
            clientRelayConnectionSocket,clientAddress = clientRelaySocket.accept()
            Thread(target=client_handler,
            args=(clientRelayConnectionSocket,clientAddress,serverAddress,serverPort),daemon=True).start()
    except KeyboardInterrupt:
        print("server stoped")
    finally:
         clientRelaySocket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    description="relay "
                )
    parser.add_argument("--relayPort", type=int, default=3456, help="relay port")
    parser.add_argument("--serverAddress",  default="127.0.0.1", help="server Address")
    parser.add_argument("--serverPort", type=int, default=2345, help="server port")
    args = parser.parse_args()
    relayPort = args.relayPort
    serverPort = args.serverPort
    serverAddress=args.serverAddress
    print(serverPort)

    run_relay(relayPort,serverAddress,serverPort)
