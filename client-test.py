from rat import RatSocket

def main():
    server_sock = RatSocket()
    print("New RatSocket construction successful!")

    server_sock.connect("127.0.0.1", 1337)
    print("RatSocket connected to 127.0.0.1:1337!")

main()