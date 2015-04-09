from rat import *
from sys import argv
from os import _exit, path, sep, getcwd

OK_SIZE = RAT_HEADER_SIZE + 2
MSG_CMD = "Ready for commands!"
MSG_CONNECTING = "Connecting to "
MSG_CONNECTED = "Connected to server!"
MSG_ENTER_CMD = "Please enter a command. \nValid choices are: " + \
    "connect, disconnect, get, post, window"
MSG_NOT_CONNECTED = "You are not connected to a server."
MSG_CONNECTED_ALREADY = "This socket is already connected or closed!"
MSG_CONNECT_FAIL = "Connection to server failed!"
ERR_INVALID_CMD = "Sorry! That's not a valid command."
ERR_PORT_ODD = "Error: Sorry! This assignment specifies an " + \
    "input port must be an even number!"
ERR_INPUT_ARGS = "Error: Address or port numbers invalid!"
ERR_INVALID_ARGS = "Syntax: fxa-client.py <local port #> " + \
    "<NetEmu IP address> <NetEmu port #>"
MSG_FILE_NOT_FOUND = "File wasn't found on the server."
MSG_GET_NO_ARG = "Please specify a filename for the get command."
MSG_POST_NO_ARG = "Please specify a filename for the post command."
MSG_SOCK_NOT_OPENED_DISCONN = "The socket was never connected " + \
"- assuming you want to quit!"
MSG_POST_NOT_FOUND = "File specified wasn't found."
MSG_POST_OK = "File sent to server!"
MSG_NOT_IMPLEMENTED = "Sorry, this command isn't implemented yet."
MSG_DISCONNECT = "Disconnected from server."
MSG_BYE = "Quitting, bye!"
CMD_PROMPT = "> "
CMD_CONNECT = "connect"
CMD_DISCONN = "disconnect"
CMD_GET = "get"
CMD_POST = "post"
CMD_WINDOW = "window"
COMMANDS = [CMD_CONNECT, CMD_DISCONN, CMD_GET, CMD_POST, CMD_WINDOW]
UDP_FILE_BUFFER_SIZE = 650000

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

    if (int(local_port) % 2 != 0):
        print(ERR_PORT_ODD)
        _exit(0)

    local_port = int(local_port)
    netemu_port = int(netemu_port)

    client_loop(local_port, netemu_ip, netemu_port)

def client_loop(local_port, netemu_ip, netemu_port):
    '''The main loop of the client.'''

    console_active = True
    client_sock = RatSocket(debug_mode=True)
    
    print(MSG_CMD)
    while console_active:
        print(MSG_ENTER_CMD)
        user_input = input(CMD_PROMPT)
        
        cmd = user_input[0:user_input.index(" ")] if " " in user_input else user_input
        args = user_input[user_input.index(" ") + 1:] if " " in user_input else ""

        if (cmd == CMD_CONNECT):
            if (client_sock.current_state == State.SOCK_UNOPENED):
                print(MSG_CONNECTING + netemu_ip + ":" + str(netemu_port) + "...")
                try:
                    client_sock.connect(netemu_ip, netemu_port, local_port=local_port)
                    print(MSG_CONNECTED)
                except Exception:
                    print(MSG_CONNECT_FAIL)
            else:
                print(MSG_CONNECTED_ALREADY)
        elif (cmd == CMD_GET):
            if (client_sock.current_state == State.SOCK_ESTABLISHED):
                if (len(args.replace(" ", "")) > 0):
                    client_sock.send(cmd + " " + args)

                    # Receive file
                    file_stream = client_sock.recv(UDP_FILE_BUFFER_SIZE)

                    if (file_stream == b"FILE_NOT_FOUND"):
                        print(MSG_FILE_NOT_FOUND)
                    else:
                        # Write contents to file
                        f = open(args, "wb")
                        f.write(file_stream)
                        f.close()
                else:
                    print(MSG_GET_NO_ARG)
            else:
                print(MSG_NOT_CONNECTED)
        elif (cmd == CMD_POST):
            if (client_sock.current_state == State.SOCK_ESTABLISHED):
                if (len(args.replace(" ", "")) > 0):
                    if handle_post(client_sock, args):
                        print(MSG_POST_OK)
                    else:
                        print(MSG_POST_NOT_FOUND)
                else:
                    print(MSG_POST_NO_ARG)
            else:
                print(MSG_NOT_CONNECTED)
        elif (cmd == CMD_WINDOW):
            print(MSG_NOT_IMPLEMENTED)
        elif (cmd == CMD_DISCONN):
            if (client_sock.current_state == State.SOCK_UNOPENED):
                print(MSG_SOCK_NOT_OPENED_DISCONN)
            else:
                client_sock.close()
                print(MSG_DISCONNECT)

            console_active = False
            print(MSG_BYE)
        else:
            print(ERR_INVALID_CMD)

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

def handle_post(client_sock, filename):
    '''Sends the file requested by a POST request, or returns False.'''

    client_sock.send(CMD_POST + " " + filename)

    # Wait for OK to send
    client_sock.recv(OK_SIZE)

    if not path.exists(getcwd() + sep + filename):
        return False

    # Open file as bytestream
    file = open(getcwd() + sep + filename, "rb")
    file_bytes = file.read()
    file.close()

    client_sock.send(file_bytes)
    return True

main()