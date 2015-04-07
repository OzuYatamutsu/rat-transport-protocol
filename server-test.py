from rat import RatSocket
from sys import argv

def main():
    server_sock = RatSocket()
    print("New RatSocket construction successful!")

    server_sock.listen("127.0.0.1", int(argv[1]), 5)
    print("RatSocket now listening for connections on 127.0.0.1:" + argv[1] + "!")

    client = server_sock.accept()
    print("RatSocket accepted connection from client!")

main()