from socket import *
import time
import argparse

def req_clock_offset(sock):


    message = "time".encode()
    t1 = time.time()

    sock.send(message)
    serverTime = sock.recv(2048).decode()
    if not serverTime:
        raise ConnectionError("server closed the connection")

    t2 = time.time()

    clock_diff = float(serverTime) - (t1+t2)/2
    rtt = t2-t1

    
    return (clock_diff,rtt)

def run_client(count,serverAddress,serverPort):
    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.settimeout(15)
    result = []

    try:
        clientSocket.connect((serverAddress,serverPort))
        for _ in range(count):
            measurement = req_clock_offset(clientSocket)
            result.append(measurement)
    except ConnectionRefusedError:
        print("server not running")
    except gaierror:
        print("can't resolve address")
    except timeout:
        print("server unreachable")
    except ConnectionError:
        print("connection lost")
    finally:
        clientSocket.close()
    return result

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                description="PING server"
            )
    parser.add_argument("--serverPort", type=int, default=2345, help="server port")
    parser.add_argument("--serverAddress",default="127.0.0.1")
    parser.add_argument("--count",type=int,default=4)
    args = parser.parse_args()
    serverPort = args.serverPort
    serverAddress=args.serverAddress
    count = args.count
    result = run_client(count,serverAddress,serverPort)

    if result:
        best = min(result, key=lambda s: s[1])
        offset, rtt = best
        print(f"the clock offset is {offset * 1000 :.3f}ms with an RTT of {rtt * 1000 :.3f} ms")



    