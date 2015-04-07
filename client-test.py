from rat import RatSocket
from sys import argv

TEST_BYTESTREAM = b"Make sure to drink your ovaltine."

def main():
    client_sock = RatSocket(True)
    print("New RatSocket construction successful!")

    client_sock.connect("127.0.0.1", int(argv[1]))
    print("RatSocket connected to 127.0.0.1:" + argv[1] + "!")

    client_sock.send(TEST_BYTESTREAM)
    print("RatSocket sent datagram!")

main()