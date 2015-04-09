from rat import *
from sys import argv
from os import _exit, getcwd, sep, path, makedirs

SERVER_OK = b"OK"
RECV_GET = "<server> Got a GET request!"
RECV_POST = "<server> Got a POST request!"
MSG_LISTENING = "<server> Now listening for connections..."
MSG_WAITING = "<server> Waiting for command from client..."
ERR_PORT_EVEN = "Error: Sorry! This assignment specifies an " + \
    "input port must be an odd number!"
ERR_INPUT_ARGS = "Error: Address or port numbers invalid!"
ERR_INVALID_ARGS = "Syntax: fxa-server.py <local port #> " + \
    "<NetEmu IP address> <NetEmu port #>"
CMD_CONNECT = "connect"
CMD_DISCONN = "disconnect"
CMD_GET = "get"
CMD_POST = "post"
CMD_WINDOW = "window"
COMMAND_BUFFER_SIZE = 64
FILE_FOLDER = getcwd() + sep + "serv_files"
POST_MAX_BUFFER = 650000

def main():
    '''The entry point of the program.'''

    # Parse command-line arguments
    if (len(argv) != 4):
        print(ERR_INVALID_ARGS)
        _exit(0)
    
    # Check arguments
    local_port = argv[1]
    netemu_ip = argv[2]
    netemu_port = argv[3]

    if not port_check(local_port) or \
    not port_check(netemu_port) or \
    not address_check(netemu_ip):
        print(ERR_INPUT_ARGS)
        _exit(0)

    if (int(local_port) % 2 != 1):
        print(ERR_PORT_EVEN)
        _exit(0)

    local_port = int(local_port)
    netemu_port = int(netemu_port)

    if not path.exists(FILE_FOLDER):
        makedirs(FILE_FOLDER)

    server_loop(local_port, netemu_ip, netemu_port)

def server_loop(local_port, netemu_ip, netemu_port):
    '''The main loop of the server.'''

    server_sock = RatSocket(debug_mode=True)
    server_sock.listen("127.0.0.1", local_port, 1)
    print(MSG_LISTENING)
    # Wait for client
    client = server_sock.accept()
    while (server_sock.current_state != State.SOCK_CLOSED):
        # Wait for command
        print(MSG_WAITING)
        server_sock.udp.settimeout(None) # No more timeout once we have a client
        cmd = server_sock.recv(RAT_HEADER_SIZE + COMMAND_BUFFER_SIZE)
        cmd = str(cmd, "utf-8")
        args = cmd[cmd.index(" ") + 1:] if " " in cmd else ""
        cmd = cmd[0:cmd.index(" ")] if " " in cmd else cmd

        # Command parsing
        if (cmd == CMD_GET):
            print(RECV_GET)
            
            handle_get(server_sock, args)
        elif (cmd == CMD_POST):
            print(RECV_POST)

            handle_post(server_sock, args)
        # Else ignore it

def handle_get(server_sock, filename):
    '''Sends the file requested by a GET request, or returns False.'''

    if not path.exists(FILE_FOLDER + sep + filename):
        server_sock.send(b"FILE_NOT_FOUND")
        return False

    # Open file as bytestream
    file = open(FILE_FOLDER + sep + filename, "rb")
    file_bytes = file.read()
    file.close()

    server_sock.send(file_bytes)
    return True

def handle_post(server_sock, filename):
    '''Downloads the file sent by a POST request, or returns False.'''

    # Hey client! OK to send!
    server_sock.send(SERVER_OK)

    try:
        file_stream = server_sock.recv(POST_MAX_BUFFER)

        # Open file as bytestream
        file = open(FILE_FOLDER + sep + filename, "wb")
        file.write(file_stream)
        file.close()

        return True
    except Exception:
        return False

def address_check(ip_addr):
    '''Checks if a given IP address is valid.'''

    try:
        octets = [int(x) for x in (ip_addr.split("."))]
        for octet in octets:
            if (octet < 0 and octet > 255):
                return False
    except Exception:
        return False

    return True

def port_check(port):
    '''Checks if a given port number is valid.'''

    try:
        port = int(port)

        # Assumed that ports 0 and 65535 are reserved
        if (port <= 0): return False
        if (port >= 65535): return False
    except Exception:
        return False

    return True

main()