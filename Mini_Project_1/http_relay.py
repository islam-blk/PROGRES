from socket import *
from threading import *
from http_utils import *
import argparse
from datetime import datetime
from uuid import uuid4

def send_error(clientRelayConnectionSocket,status,reason,body,content_type):
    try:
        response = build_response(status,reason,body,content_type)
        clientRelayConnectionSocket.sendall(response)
    except OSError:
        pass

def build_log(log_type, request_id, client_ip,uri,
              status="", body_size=""):
    timestamp = datetime.now().isoformat(timespec="milliseconds")

    fields = [
        timestamp,
        request_id,
        clean_field(log_type),
        clean_field(client_ip),
        clean_field(uri),
        str(status),
        str(body_size)
    ]

    return "\t".join(fields)

def client_handler(clientRelayConnectionSocket,clientAddress,serverAddress,serverPort,cache,log,ban):
    relayServerSocket = None
    try:
        try:
            print("handling client",clientAddress)

            clientRelayConnectionSocket.settimeout(10)
            request = read_request(clientRelayConnectionSocket)
            clientRelayConnectionSocket.settimeout(None)
            
            method, uri, version, req_headers = parse_request(request)
            client_ip = req_headers.get("x-forwarded-for", clientAddress[0])
            request_id = uuid4().hex
            if method == "GET" and log:
                  write_log("relay.log", build_log(
                 "REQUEST", request_id, client_ip, uri
                 ))
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
            is_banned = False
            for site in ban:
                if site in uri.lower():
                      is_banned = True
            if  method == "GET" and is_banned:
                write_log("forbidden.log", client_ip)
                send_error(clientRelayConnectionSocket,403,"Forbidden",b"Forbidden","text/plain")
                return
            else:
                cache_result = None
                if method == "GET" and cache:
                    cache_result = cache_read(uri)
                if cache_result: 
                    print(f"cache hit on uri {uri}")
                    response = cache_result
                    response_received = True
                else:
                    if cache:
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
                    response_received = bool(response)

                    if not response:
                        response = build_response(502,"Bad Gateway",b"502 Bad Gateway","text/html")
                        

                    status, res_headers, body = split_response(response)
                    
                
                    if status == 200 and method == 'GET' and cache :
                        cache_put(uri,response)

                
                try:
                    

                    if ban and method == "GET":
                        response, was_censored = censor_response(response, ban)
                        if was_censored:
                             write_log("forbidden.log", client_ip)
                    status, res_headers, body = split_response(response)
                    if response_received and method == "GET" and body and log:
                        write_log("relay.log",
                                    build_log("RESPONSE", request_id, client_ip , uri,status, len(body)))
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
                print("server unreachable timeout")
                send_error(clientRelayConnectionSocket,504,"Gateway Timeout",b"504 Bad Gateway: server unreachable timeout","text/html")
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
                                                    
    

def run_relay(relayPort,serverAddress,serverPort,cache,log,ban):
    clientRelaySocket = socket(AF_INET,SOCK_STREAM)

    try:
        clientRelaySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        clientRelaySocket.bind(('',relayPort))
        clientRelaySocket.listen(5)
        clientRelaySocket.settimeout(1)

        print(f'Relay ready!!!, listening on port {str(relayPort)}\n' )
        if cache:
             print("cache on")
        if log:
                     print("log on")

    
        while True:
            try:
                clientRelayConnectionSocket,clientAddress = clientRelaySocket.accept()
                Thread(target=client_handler,
                args=(clientRelayConnectionSocket,clientAddress,serverAddress,serverPort,cache,log,ban),daemon=True).start()
            except timeout:
                    continue       

    except KeyboardInterrupt:
            print("relay stopped")
    finally:
            clientRelaySocket.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                         description="relay ")
    
    parser.add_argument("--relayPort", type=int, default=3456, help="relay port")
    parser.add_argument("--serverAddress",  default="127.0.0.1", help="server Address")
    parser.add_argument("--serverPort", type=int, default=8000, help="server port")
    parser.add_argument("--cache",action="store_true",help="add this argument to activate cache on the relay")
    parser.add_argument("--log",action="store_true",help="add this argument to activate loggin GET requests ")
    parser.add_argument("--ban",help="provide a txt file of banned URIs")

    args = parser.parse_args()
    relayPort = args.relayPort
    serverPort = args.serverPort
    serverAddress = args.serverAddress
    cache = args.cache
    log = args.log

    
    ban = load_banned_sites(args.ban) if args.ban else []
    

    run_relay(relayPort,serverAddress,serverPort,cache,log,ban)