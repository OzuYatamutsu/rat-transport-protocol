from enum import Enum
from socket import socket

# Header sizes, in bytes
RAT_HEADER_SIZE = 8
UDP_HEADER_SIZE = 8

## RAT default values
RAT_PAYLOAD_SIZE = 512

## RAT timers (in seconds)
RAT_REPLY_TIMEOUT = 4
RAT_BYE_TIMEOUT = RAT_REPLY_TIMEOUT / 4

## RAT messages
ERR_STATE = "Error: cannot perform operation " + \
"in current connection state!"
ERR_HEADER_INVALID = "Error: RAT header size mismatch " + \
"header may be malformed!"
ERR_NUM_OUT_OF_RANGE = "Error: number out of range!"

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

## RAT header flags
class Flag(Enum):
    '''The collection of header flags in the RAT protocol.'''
    ACK = 0
    NACK = 1
    SWIN = 2
    RST = 3
    ALI = 4
    HLO = 5
    BYE = 6
    EXP = 7
    ORDER = [ACK, NACK, SWIN, RST, ALI, HLO, BYE, EXP]

class RatSocket:
    '''A connection socket in the RAT protocol.'''

    def __init__(self):
        '''Constructs a new RAT protocol socket.'''

        self.current_state = SOCK_UNOPENED

        # Underlying UDP socket
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.settimeout(RAT_REPLY_TIMEOUT)

        self.stream_id = 0
        self.seq_num = 0
        self.window_size = 0
        self.nack_queue = []

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

        self.remote_addr = (address, port)

        # Send HLO
        segment = construct_header(0, flag_set([Flag.HLO]), 0)
        udp.sendto(segment, self.remote_addr)
        self.current_state = State.SOCK_HLOSENT

        # Receive HLO, ACK and set stream_id and seq_num
        segment = decode_rat_header(udp.recvfrom(RAT_HEADER_SIZE))
        self.stream_id = hlo_ack["stream_id"]
        self.seq_num = hlo_ack["seq_num"]

        # Send ACK
        segment = construct_header(0, flag_set([Flag.ACK]), 0)
        udp.sendto(segment, self.remote_addr)

        self.current_state = State.SOCK_ESTABLISHED

    def send(bytes):
        '''Sends a byte-stream.'''

        send_queue = []

        while (len(bytes) != 0):
            data = bytes[0:RAT_PAYLOAD_SIZE]
            bytes = bytes[RAT_PAYLOAD_SIZE:]
            send_queue.append(construct_header(len(data), 0, 0) + data)
            self.seq_num = self.seq_num + 1

        while (len(send_queue) > 0):
            window_remain = window_size

            while (len(send_queue) > 0 and window_remain > 0):
                window_remain = window_remain - 1
                udp.sendto(send_queue[0], self.remote_addr)
                del send_queue[0]

            # TODO: ACKs at end of window

    def recv(buffer_size):
        '''Reads a given amount of data from an established socket.'''

        state_check([SOCK_ESTABLISHED, SOCK_BYESENT, SOCK_BYERECV])
        bytes_read = 0
        recv_queue = {}
        segment = b""
        segments_recv = 0
        buffer_ok = True

        try:
            while (bytes_read < buffer_size):
                while (segments_recv < self.window_size):
                    header = decode_rat_header(
                        udp.recvfrom(RAT_HEADER_SIZE))
                    integrity_check(header)
                    flags = flag_decode(header)
                    udp_length = 0
                
                    while (udp_length < header["length"]):
                        segment = segment + udp.recvfrom(header["length"])
                        bytes_read = bytes_read + header["length"]
            
                    if (bytes_read > buffer_size):
                        # If there's no room in the buffer, discard and NACK
                        bytes_read = buffer_size
                        raise IOError

                    recv_queue[header["seq_num"]] = segment
                    seq_num = seq_num + 1
                    # TODO: Handle flags

                # TODO: ACK/NACK

        except IOError:
            nack_queue.append(seq_num)
            nack(seq_num)

    def close():
        '''Attempts to cleanly close a socket and shut down the connection 
        stream. Sockets which are closed cannot be reopened or reused.'''



        pass # TODO: implement

    def ack():
        pass

    def nack():
        pass

    def decode_rat_header(byte_stream):
        '''Decodes a raw byte-stream as a RAT header and 
        returns the header data.'''

        if (len(byte_stream) != RAT_HEADER_SIZE):
            raise IOError(ERR_HEADER_INVALID)

        stream_id = int(byte_stream[0:2])
        seq_num = int(byte_stream[2:4])
        length = int(byte_stream[4:6])
        flags = str(byte_stream[6])
        offset = int(byte_stream[7])

        return {"stream_id": stream_id, "seq_num": seq_num, 
                "length": length, "flags": flags, "offset": offset}

    def state_check(state):
        '''Raises an error if this socket is attempting 
        to perform an operation in an inappropriate state.'''

        if (self.current_state not in state):
            raise IOError(ERR_STATE)

    def integrity_check(header):
        '''Raises an error if this header is not destined 
        for the current stream.'''

        if header[0] != self.stream_id:
            raise IOError

    def flag_decode(header):
        '''Returns the flags set in a RAT header.'''

        flag_list = []

        for bit in range(0, 8):
            if bit is "1":
                flag_list.append(Flag.ORDER[bit])

        return flag_list

    def flag_set(flags):
        '''Returns a byte-stream corresponding to the given flags provided.'''

        output = b""
        for flag in Flag.ORDER:
            if (flag in flags):
                output = output + b"1"
            else:
                output = output + b"0"

        return output

    def zero_pad(num, length):
        '''Adds leading zeros to num to pad it to given length.'''
        
        padding = length - len(str(num))
        if (padding < 0):
            raise AssertionError(ERR_NUM_OUT_OF_RANGE)

        return (padding * '0') + str(num)
        
    def construct_header(length, flags, offset):
        '''Constructs an 8-byte long RAT header.'''

        header = b""

        # Add stream_id
        header = header + zero_pad(self.stream_id, 16)

        # Add seq_num
        header = header + zero_pad(self.seq_num, 16)

        # Add length
        header = header + zero_pad(length, 16)

        # Add flags
        header = header + zero_pad(flags, 8)

        # Add offset
        header = header + zero_pad(offset, 8)

        return header