from enum import Enum
from socket import socket
import threading

## RAT default values

## RAT timers (in seconds)
RAT_REPLY_TIMEOUT = 4
RAT_BYE_TIMEOUT = RAT_REPLY_TIMEOUT / 4

## RAT messages
ERR_STATE = "Error: cannot perform operation " + \
"in current connection state!"

## RAT connection states
class State(Enum):
    '''The collection of connection states in the RAT protocol.'''

    SOCK_UNOPENED = 0
    SOCK_SERVOPEN = 1
    SOCK_HLOSENT = 2
    SOCK_HLORECV = 3
    SOCK_ESTABLISHED = 4
    SOCK_BYESENT = 5
    SOCK_BYERECV = 6
    SOCK_CLOSED = 7

class RatSocket:
    '''A connection socket in the RAT protocol.'''

    # Threading lock
    queue_lock = threading.Lock()

    def __init__(self):
        '''Constructs a new RAT protocol socket.'''

        self.current_state = SOCK_UNOPENED

        # Underlying UDP socket
        self.udp = socket(socket.AF_INET, 
                          socket.SOCK_DGRAM)

        # Threading lock

    def listen(address, port, num_connections):
        '''Listens for a given maximum number of 
       connections on a given address and port.'''

        state_check(SOCK_UNOPENED)
        udp.bind((address, port))

        self.num_connections = num_connections
        self.sock_queue = []
        self.current_state = SOCK_SERVOPEN
        self.obey_keepalives = True

    def accept():
        '''Accepts a connection from a connection queue and 
        returns a new client socket to use. This removes the 
        connection from the connection queue. If there are no 
        connections in the queue, this is a blocking I/O call, 
        and the program will sleep until a connection is available 
        to accept. The client socket will have an established 
        connection to the client.'''

        state_check(SOCK_SERVOPEN)
        while (len(sock_queue) == 0):
            pass
            # Release the lock
        pass # TODO: implement

    def allow_keepalives(value):
        '''Directs the socket to follow or ignore keep-alive messages.'''

        self.obey_keepalives = value

    def connect(address, port, send_keepalives=False):
        '''Attempts to connect to a server socket at a given port 
        and address. If successful, the current socket will have an 
        established connection to the server. An optional keep-alive 
        directive can be set (default False) that directs this client 
        to send keep-alive messages.'''

        pass # TODO: implement

    def send(bytes):
        '''Sends a byte-stream.'''

        pass # TODO: implement

    def recv(buffer_size):
        '''Reads a given amount of data from an established socket.'''

        pass # TODO: implement

    def close():
        '''Attempts to cleanly close a socket and shut down the connection 
        stream. Sockets which are closed cannot be reopened or reused.'''

        pass # TODO: implement

    def state_check(state):
        '''Raises an error if this socket is attempting 
        to perform an operation in an inappropriate state.'''

        if (self.current_state not in state):
            raise IOError(ERR_STATE)