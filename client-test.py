from rat import RatSocket
from sys import argv

def main():
    server_sock = RatSocket()
    print("New RatSocket construction successful!")

    result = server_sock.connect("127.0.0.1", int(argv[1]))
    if result is not False: print("RatSocket connected to 127.0.0.1:" + argv[1] + "!")
    else: print("RatSocket connection reply failure!")

main()