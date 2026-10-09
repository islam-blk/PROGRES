from socket import *
from threading import *
import argparse

def forward(src,dest,direction):
    try:
        while True:
            message = src.recv(2048)
            if message == b'':
                break
            print(f"{direction} {len(message)} bytes ")
            dest.sendall(message)
    except OSError as e:
         print(f"{direction} error happened {e}")
    dest.shutdown(SHUT_WR)
   

def client_handler(clientRelayConnectionSocket:socket,clientAddress,serverAddress,serverPort):
    try:
        print("handling client",clientAddress)
        relayServerSocket = socket(AF_INET,SOCK_STREAM)
        relayServerSocket.connect((serverAddress,serverPort))
        print(f"connected to server {serverAddress}:{serverPort}")
        t = Thread(target=forward,
                args=(relayServerSocket,clientRelayConnectionSocket,"server -> client"),daemon=True)
        t.start()
        forward(clientRelayConnectionSocket,relayServerSocket,"client -> server")
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
        clientRelaySocket.settimeout(1)
        print('Relay ready!!!, listning on port ' + str(relayPort))
        
        while True:
            try:
                clientRelayConnectionSocket,clientAddress = clientRelaySocket.accept()
                Thread(target=client_handler,
                args=(clientRelayConnectionSocket,clientAddress,serverAddress,serverPort),daemon=True).start()
            except timeout:
                 continue
                 
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
    

    run_relay(relayPort,serverAddress,serverPort)
