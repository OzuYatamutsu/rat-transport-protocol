from rat import RatSocket, RAT_HEADER_SIZE
from sys import argv

TEST_BYTESTREAM = b"Make sure to drink your ovaltine."
TEST_BYTESTREAM2 = b"All commit and no push makes Jinhai a big risk"
TEST_BYTESTREAM3 = b"If you have 8 AM classes, I feel bad for ya son"
TEST_BYTESTREAM4 = b"I've got 99 problems, but they start at 1"
TEST_LONGSTREAM = b"""This is a long bytestream that must be split into multiple segments.
This is line two of a long bytestream that must be split into multiple segments.
This is line three of a long bytestream that must be split into multiple segments.
This is line four of a long bytestream that must be split into multiple segments."""

send_queue = [TEST_BYTESTREAM, TEST_BYTESTREAM2, TEST_BYTESTREAM3, 
              TEST_BYTESTREAM4, TEST_LONGSTREAM]

def main():
    server_sock = RatSocket(True)
    print("New RatSocket construction successful!")

    server_sock.listen("127.0.0.1", int(argv[1]), 5)
    print("RatSocket now listening for connections on 127.0.0.1:" + argv[1] + "!")

    client = server_sock.accept()
    if client is not False: print("RatSocket accepted connection from client!")
    else: print("Error: RatSocket didn't receive ACK response!")

    for item in send_queue:
        client_sock.send(TEST_BYTESTREAM)
        print("RatSocket sent stream " + str(send_queue.index(item) + 1) + "to server!")

main()