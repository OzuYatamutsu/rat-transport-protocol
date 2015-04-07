from rat import RatSocket
from sys import argv

def main():
    server_sock = RatSocket(True)
    print("New RatSocket construction successful!")

    server_sock.connect("127.0.0.1", int(argv[1]))
    print("RatSocket connected to 127.0.0.1:" + argv[1] + "!")

main()