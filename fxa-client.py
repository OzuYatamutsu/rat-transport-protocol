from rat import *
from sys import argv
from os import _exit

MSG_CMD = "Ready for commands!"
MSG_CONNECTING = "Connecting to "
MSG_CONNECTED = "Connected to server!"
MSG_ENTER_CMD = "Please enter a command. \nValid choices are: " + \
    "connect, disconnect, get, post, window"
MSG_CONNECT_FAIL = "Connection to server failed!"
ERR_INVALID_CMD = "Sorry! That's not a valid command."
ERR_PORT_ODD = "Error: Sorry! This assignment specifies an " + \
    "input port must be an even number!"
ERR_INPUT_ARGS = "Error: Address or port numbers invalid!"
ERR_INVALID_ARGS = "Syntax: fxa-client.py <local port #> " + \
    "<NetEmu IP address> <NetEmu port #>"
MSG_SOCK_NOT_OPENED_DISCONN = "The socket was never connected " + \
"- assuming you want to quit!"
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
            print(MSG_CONNECTING + netemu_ip + ":" + str(netemu_port) + "...")
            try:
                client_sock.connect(netemu_ip, netemu_port, local_port=local_port)
                print(MSG_CONNECTED)
            except Exception:
                print(MSG_CONNECT_FAIL)
        elif (cmd == CMD_GET):
            pass
        elif (cmd == CMD_POST):
            print(MSG_NOT_IMPLEMENTED)
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

main()