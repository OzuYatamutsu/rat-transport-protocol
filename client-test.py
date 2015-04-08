from rat import RatSocket, RAT_HEADER_SIZE
from sys import argv

TEST_BYTESTREAM = b"Make sure to drink your ovaltine."
TEST_BYTESTREAM2 = b"All commit and no push makes Jinhai a big risk"
TEST_BYTESTREAM3 = b"If you have 8 AM classes, I feel bad for ya son"
TEST_BYTESTREAM4 = b"I've got 99 problems, but they start at 1"
TEST_LONGSTREAM = b"""This is a long bytestream that must be split into multiple segments.
This is line two of a long bytestream that must be split into multiple segments.
This is line three of a long bytestream that must be split into multiple segments.
This is line four of a long bytestream that must be split into multiple segments.
This is line five of a long bytestream that must be split into multiple segments.
This is line six of a long bytestream that must be split into multiple segments.
This is line seven of a long bytestream that must be split into multiple segments.
This is line eight of a long bytestream that must be split into multiple segments.
This is line nine of a long bytestream that must be split into multiple segments."""

recv_queue = [TEST_BYTESTREAM, TEST_BYTESTREAM2, TEST_BYTESTREAM3, 
              TEST_BYTESTREAM4, TEST_LONGSTREAM]

def main():
    client_sock = RatSocket(True)
    print("New RatSocket construction successful!")

    client_sock.connect("127.0.0.1", int(argv[1]))
    print("RatSocket connected to 127.0.0.1:" + argv[1] + "!")
    print("Local bind: " + str(client_sock.local_addr))
    print("Remote bind: " + str(client_sock.remote_addr))

    for item in recv_queue:
        test_data = client_sock.recv(len(item) + RAT_HEADER_SIZE)
        if test_data == item: print("RatSocket successfully receieved datagram " + 
                                    str(recv_queue.index(item) + 1) + " from server!")

    print("Now closing the connection.")
    client_sock.close()

main()