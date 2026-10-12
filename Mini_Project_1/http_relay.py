from socket import *
from threading import *
from http_utils import *
import argparse

def send_error(clientRelayConnectionSocket,status,reason,body,content_type):
    try:
        response = build_response(status,reason,body,content_type)
        clientRelayConnectionSocket.sendall(response)
    except OSError:
        pass

def client_handler(clientRelayConnectionSocket,clientAddress,serverAddress,serverPort):
    relayServerSocket = None
    try:
        try:
            print("handling client",clientAddress)

            clientRelayConnectionSocket.settimeout(10)
            request = read_request(clientRelayConnectionSocket)
            clientRelayConnectionSocket.settimeout(None)
            
            method, uri, version, req_headers = parse_request(request)
        except ConnectionError:
            print("client disconnected")
            return
        except timeout:
            print("client timeout")
            return
        except ValueError:
            send_error(clientRelayConnectionSocket,400,"Bad request",b"Bad request: malformed request","text/html")
            return
        try:
            cache_result = None
            if method == "GET":
                cache_result = cache_read(uri)
            if cache_result: 
                print(f"cache hit on uri {uri}")
                response = cache_result
            else:
                print(f"cache miss on uri {uri}")

                relayServerSocket = socket(AF_INET,SOCK_STREAM)
                relayServerSocket.connect((serverAddress,serverPort))
                print(f"connected to server {serverAddress}:{serverPort}")

                if not req_headers.get("x-forwarded-for"):
                    req_headers["x-forwarded-for"] = clientAddress[0]

                request = build_request(method, uri, version,req_headers)

                relayServerSocket.sendall(request)

                relayServerSocket.settimeout(30)
                response = read_response(relayServerSocket)

                if response == b'':
                    response = build_response(502,"Bad Gateway",b"502 Bad Gateway","text/html")
                    

                status, res_headers, body = split_response(response)
            
                if status == 200 and method == 'GET' :
                    cache_put(uri,response)
            try:
                clientRelayConnectionSocket.sendall(response)
            except OSError:
                 print("client left")
        
        except ConnectionRefusedError:
                print("server unreachable")
                send_error(clientRelayConnectionSocket,502,"Bad Gateway",b"502 Bad Gateway: server unreachable","text/html")
        except gaierror:
                print("error in server address")
                send_error(clientRelayConnectionSocket,502,"Bad Gateway",b"502 Bad Gateway: error in server address","text/html")
        except timeout:
                print("server unreachable timeou")
                send_error(clientRelayConnectionSocket,502,"Bad Gateway",b"502 Bad Gateway: server unreachable timeout","text/html")
        except ValueError:
                print("Malformed response")
                send_error(clientRelayConnectionSocket,502,"Bad Gateway",b"502 Bad Gateway: Malformed input","text/html")
        except ConnectionError:
                print("connection error with the server")
                send_error(clientRelayConnectionSocket,502,"Bad Gateway",b"502 Bad Gateway: connection error","text/html")
    finally:
        clientRelayConnectionSocket.close()
        if relayServerSocket:
            relayServerSocket.close()
                                                    
    

def run_relay(relayPort,serverAddress,serverPort):
    clientRelaySocket = socket(AF_INET,SOCK_STREAM)
    
    clientRelaySocket.bind(('',relayPort))
    clientRelaySocket.listen(5)
    clientRelaySocket.settimeout(1)

    print('Relay ready!!!, listning on port ' + str(relayPort))

    try:
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

