from enum import Enum
from socket import socket, AF_INET, SOCK_DGRAM
from random import randrange

## Other values
RAT_MAX_SEQ_NUM = 65535
RAT_MAX_STREAM_ID = 65535
RAT_RETRY_TIMES = 5
# Max number of 16 bit overhead words in payload (16 * 255)
RAT_MAX_OVERHEAD_BUFFER = 4080

## Header sizes, in bits
RAT_HEADER_SIZE = 64
UDP_HEADER_SIZE = 64

## RAT default values
RAT_PAYLOAD_SIZE = 512
RAT_DEFAULT_WINDOW = 5

## RAT timers (in seconds)
RAT_REPLY_TIMEOUT = 4
RAT_BYE_TIMEOUT = RAT_REPLY_TIMEOUT / 4

## RAT messages
ERR_PREFIX = "<error> "
DEBUG_PREFIX = "<debug> "
ERR_STATE = ERR_PREFIX + "Cannot perform operation " + \
"in current connection state!"
ERR_HEADER_INVALID = ERR_PREFIX + "RAT header size mismatch; " + \
"header may be malformed!"
ERR_MISALIGNED_WORDS = ERR_PREFIX + "Overhead data is not aligned to 16 bits!"
ERR_NUM_OUT_OF_RANGE = ERR_PREFIX + "Number out of range!"
DEBUG_LISTEN = DEBUG_PREFIX + "Now listening for connections (SOCK_SERVOPEN)."
DEBUG_LISTEN_HLO = DEBUG_PREFIX + "Waiting for HLO... (SOCK_SERVOPEN)"
DEBUG_CLI_SENT_HLO = DEBUG_PREFIX + "Sending HLO (SOCK_HLOSENT)."
DEBUG_CLI_RECV_HLOACK = DEBUG_PREFIX + "Receieved HLO, ACK from server (SOCK_ESTABLISHED)."
DEBUG_CLI_SENT_ACK = DEBUG_PREFIX + "Sent ACK (SOCK_ESTABLISHED)."
DEBUG_SERV_RECV_HLO = DEBUG_PREFIX + "Received HLO (SOCK_HLORECV)."
DEBUG_SERV_SENT_HLOACK = DEBUG_PREFIX + "Sent HLO, ACK to client."
DEBUG_SERV_RECV_ACK = DEBUG_PREFIX + "Receieved ACK (SOCK_ESTABLISHED)."
DEBUG_SENT_ACK = DEBUG_PREFIX + "Sent ACK."
DEBUG_RECV_ACK = DEBUG_PREFIX + "Receieved ACK."
DEBUG_SENT_NACK = DEBUG_PREFIX + "Sent NACK."
DEBUG_RECV_NACK = DEBUG_PREFIX + "Receieved NACK."
DEBUG_SENT_SEQ = DEBUG_PREFIX + "Sent segment #."
DEBUG_RECV_SEQ = DEBUG_PREFIX + "Received segment #."
DEBUG_RETRY_FAIL = DEBUG_PREFIX + "Too many failed retransmits; giving up."

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

RAT_FLAG_ORDER = [Flag.ACK, Flag.NACK, Flag.SWIN, Flag.RST, 
                  Flag.ALI, Flag.HLO, Flag.BYE, Flag.EXP]

class RatSocket:
    '''A connection socket in the RAT protocol.'''

    def __init__(self, debug_mode=False):
        '''Constructs a new RAT protocol socket.'''

        self.current_state = State.SOCK_UNOPENED

        # Underlying UDP socket
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.settimeout(None)

        # State overhead
        self.stream_id = 0
        self.seq_num = 0
        self.window_size = 0

        # Other values
        self.remote_addr = ("localhost", 0)
        self.active_streams = []
        self.sock_queue = []
        self.obey_keepalives = True
        self.num_connections = 0
        self.debug_mode = debug_mode

    def listen(self, address, port, num_connections):
        '''Listens for a given maximum number of 
       connections on a given address and port.'''

        self.state_check(State.SOCK_UNOPENED)

        self.udp.bind((address, port))
        self.num_connections = num_connections
        self.current_state = State.SOCK_SERVOPEN

        if self.debug_mode: print(DEBUG_LISTEN)

    def accept(self):
        '''Accepts a connection from a connection queue and 
        returns a new client socket to use. This removes the 
        connection from the connection queue. If there are no 
        connections in the queue, this is a blocking I/O call, 
        and the program will sleep until a connection is available 
        to accept. The client socket will have an established 
        connection to the client.'''

        self.state_check(State.SOCK_SERVOPEN)
        retry_times = RAT_RETRY_TIMES

        # Start listening for HLO
        if self.debug_mode: print(DEBUG_LISTEN_HLO)

        hlo, address = self.udp.recvfrom(RAT_HEADER_SIZE)
        hlo = self.decode_rat_header(hlo)

        if (Flag.HLO in self.flag_decode(hlo["flags"])):
            # Timeout begins now!
            self.udp.settimeout(RAT_REPLY_TIMEOUT)
            if self.debug_mode: print(DEBUG_SERV_RECV_HLO)

            # Create new client socket and generate stream_id
            client = RatSocket()
            client.remote_addr = address
            client.current_state = State.SOCK_HLORECV
            client.stream_id = randrange(1, RAT_MAX_STREAM_ID)
            client.window_size = RAT_DEFAULT_WINDOW
            # Debug
            self.stream_id = client.stream_id

            self.active_streams.append(client)
            client.seq_num = client.seq_num + 1

            # Send ACK, HLO
            ack = {}
            while (retry_times != 0 and not self.is_valid_flagmsg(ack, Flag.ACK)):
                try:
                    if self.debug_mode: print(DEBUG_SERV_SENT_HLOACK)
                    response = client.construct_header(0, self.flag_set([Flag.ACK, Flag.HLO]), 0)
                    self.udp.sendto(response, client.remote_addr)

                    # Wait for ACK
                    ack = self.udp.recvfrom(RAT_HEADER_SIZE)[0]
                    ack = self.decode_rat_header(ack)
                except Exception:
                    retry_times = retry_times - 1

            if (retry_times == 0):
                if self.debug_mode: print(DEBUG_RETRY_FAIL)
                return False

            # Connection established successfully
            if self.debug_mode: print(DEBUG_SERV_RECV_ACK)
            client.current_state = State.SOCK_ESTABLISHED
            self.current_state = State.SOCK_ESTABLISHED
            self.seq_num = 1

            return client
        else: return False # HLO not in flags

    def allow_keepalives(self, value):
        '''Directs the socket to follow or ignore keep-alive messages.'''

        self.obey_keepalives = value

    def connect(self, address, port, send_keepalives=False):
        '''Attempts to connect to a server socket at a given port 
        and address. If successful, the current socket will have an 
        established connection to the server. An optional keep-alive 
        directive can be set (default False) that directs this client 
        to send keep-alive messages.'''

        # Timeout begins now!
        self.udp.settimeout(RAT_REPLY_TIMEOUT)
        self.remote_addr = (address, port)

        # Send HLO
        if self.debug_mode: print(DEBUG_CLI_SENT_HLO)

        segment = {}
        retry_times = RAT_RETRY_TIMES

        while (retry_times != 0 and not self.is_valid_flagmsg(segment, Flag.HLO) and not 
               self.is_valid_flagmsg(segment, Flag.ACK)):
            try:
                segment = self.construct_header(0, self.flag_set([Flag.HLO]), 0)
                self.udp.sendto(segment, self.remote_addr)
                self.current_state = State.SOCK_HLOSENT

                # Receive ACK, HLO and set stream_id and seq_num
                segment = self.udp.recvfrom(RAT_HEADER_SIZE)[0]
                segment = self.decode_rat_header(segment)
                self.stream_id = segment["stream_id"]
                self.seq_num = segment["seq_num"]
                self.window_size = RAT_DEFAULT_WINDOW
                if self.debug_mode: print(DEBUG_CLI_RECV_HLOACK)
            except Exception:
                retry_times = retry_times - 1

        # Send ACK
        if self.debug_mode: print(DEBUG_CLI_SENT_ACK)

        segment = self.construct_header(0, self.flag_set([Flag.ACK]), 0)
        self.seq_num = 1
        self.udp.sendto(segment, self.remote_addr)
        self.current_state = State.SOCK_ESTABLISHED

    def send(self, byte_stream):
        '''Sends a byte-stream.'''

        send_queue = {}

        while (len(byte_stream) != 0):
            data = byte_stream[0:RAT_PAYLOAD_SIZE]
            byte_stream = byte_stream[RAT_PAYLOAD_SIZE:]

            if (len(byte_stream) == 0):
                send_queue[self.seq_num] = self.construct_header(len(data), 
                    self.flag_set([Flag.ACK]), 0) + data
            else:
                send_queue[self.seq_num] = self.construct_header(len(data), 0, 0) + data
            self.seq_num = self.seq_num + 1

        list_queue = list(send_queue)
        list_queue.sort()
        while (len(list_queue) > 0):
            window_queue = list_queue[0:self.window_size]

            for segment in window_queue:
                self.udp.sendto(send_queue[segment], self.remote_addr)
                if self.debug_mode: print(DEBUG_SENT_SEQ.replace("#", str(segment)))

            # Wait for ACK or NACK
            segment_full = self.udp.recvfrom(RAT_MAX_OVERHEAD_BUFFER)[0]
            segment = self.decode_rat_header(segment)[0:64]

            # TODO: Other flags
            if (Flag.ACK in flag_decode(segment["flags"])):
                if self.debug_mode: print(DEBUG_RECV_ACK)
                if (segment["seq_num"] == self.seq_num):
                    self.seq_num = self.seq_num + 1

                else:
                    # PROBLEM HERE - SEQ_NUM MISMATCH
                    pass
            elif (Flag.NACK in flag_decode(segment["flags"])):
                if self.debug_mode: print(DEBUG_RECV_NACK)
                nack_queue = data_decode(segment_full[64 : (16 * segment["offset"])])

                # Retransmit NACKed sequence numbers
                window_queue = [nacked for nacked in window_queue if nacked not in nack_queue]
                self.seq_num = self.seq_num + 1

            else:
                # PROBLEM HERE - SEGMENT NOT ACK OR NACK
                pass

            # Remove from buffer
            list_queue = [unsent for unsent in list_queue if unsent not in window_queue]

    def recv(self, buffer_size):
        '''Reads a given amount of data from an established socket.'''

        self.state_check([State.SOCK_ESTABLISHED, State.SOCK_BYESENT, State.SOCK_BYERECV])
        bytes_read = 0
        recv_queue = {}
        nack_queue = []
        out_of_order_queue = []
        segment = b""
        segments_recv = 0
        buffer_ok = True
        current_window = self.window_size

        full_seg = self.udp.recvfrom(buffer_size)[0]
        while (len(full_seg) > 0):
            header = full_seg[0:RAT_HEADER_SIZE]
            header = self.decode_rat_header(header)
            if not self.integrity_check(header): 
                nack_queue.append(header["seq_num"])
            else:
                if self.debug_mode: print(DEBUG_RECV_SEQ.replace("#", str(header["seq_num"])))
                if (self.seq_num != header["seq_num"]):
                    if (header["seq_num"] in out_of_order_queue):
                        out_of_order_queue.remove(header["seq_num"])
                    else:
                        out_of_order_queue.append(self.seq_num)
                        self.seq_num = header["seq_num"] + 1
                else:
                    self.seq_num = self.seq_num + 1

                recv_queue[header["seq_num"]] = full_seg[RAT_HEADER_SIZE : (RAT_HEADER_SIZE + header["length"])]
                full_seg = full_seg[(RAT_HEADER_SIZE + header["length"]):]

            # At end of window
            nack_queue = nack_queue + out_of_order_queue
            if (len(nack_queue) > 0):
                if self.debug_mode: print(DEBUG_SENT_NACK)
                self.nack(nack_queue)
            else:
                if self.debug_mode: print(DEBUG_SENT_ACK)
                self.ack()

        # Reorder data and return
        out_queue = list(recv_queue)
        out_queue.sort()

        output = b""
        for seg_data in out_queue:
            output = output + recv_queue[seg_data]

        return output

    def close(self):
        '''Attempts to cleanly close a socket and shut down the connection 
        stream. Sockets which are closed cannot be reopened or reused.'''

        # Timeout begins now!
        self.udp.settimeout(RAT_BYE_TIMEOUT)

        # Send BYE
        if self.debug_mode: print(DEBUG_CLI_SENT_HLO)

        while (retry_times != 0):
            try:
                segment = self.construct_header(0, self.flag_set([Flag.BYE]), 0)
                self.udp.sendto(segment, self.remote_addr)
                self.current_state = State.SOCK_BYESENT
            except Exception:
                retry_times = retry_times - 1

        # Remaining is handled by recv() and close_halfopen()

    def ack(self):
        '''Sends an acknowledgement that everything 
        in the current window was received.'''

        ack = self.construct_header(0, self.flag_set([Flag.ACK]), 0)
        retry_times = RAT_RETRY_TIMES
        sent = False

        while (retry_times != 0 and not sent):
            try:
                self.udp.sendto(ack, self.remote_addr)
                sent = True
            except Exception:
                retry_times = retry_times - 1
        self.seq_num = self.seq_num + 1

    def nack(self, seq_nums):
        '''Sends a notice that the data associated with 
        the given sequence numbers was not received.'''

        seq_nums = list(self.zero_pad(x) for x in seq_nums)
        length = len(''.join(seq_nums))

        # Sanity check
        if ((length % 16) != 0):
            raise IOError(ERR_MISALIGNED_WORDS)


        ack = self.construct_header(length, self.flag_set([Flag.NACK]), len(seq_nums))
        ack = ack + ''.join(seq_nums)
        retry_times = RAT_RETRY_TIMES
        sent = False

        while (retry_times != 0 and not sent):
            try:
                self.udp.sendto(ack, self.remote_addr)
                sent = True
            except Exception:
                retry_times = retry_times - 1
        self.seq_num = self.seq_num + 1

    def decode_rat_header(self, byte_stream):
        '''Decodes a raw byte-stream as a RAT header and 
        returns the header data.'''

        if (len(byte_stream) != RAT_HEADER_SIZE):
            raise IOError(ERR_HEADER_INVALID)

        stream_id = int(byte_stream[0:16], 2)
        seq_num = int(byte_stream[16:32], 2)
        length = int(byte_stream[32:48], 2)
        flags = str(byte_stream[48:56], "utf-8")
        offset = int(byte_stream[56:64], 2)

        return {"stream_id": stream_id, "seq_num": seq_num, 
                "length": length, "flags": flags, "offset": offset}

    def state_check(self, state):
        '''Raises an error if this socket is attempting 
        to perform an operation in an inappropriate state.'''

        if (self.current_state != state):
            if (self.current_state not in state):
                raise IOError(ERR_STATE)

    def integrity_check(self, header):
        '''Returns False if this header is not destined 
        for the current stream.'''

        if header["stream_id"] != self.stream_id:
            return False
        return True

    def flag_decode(self, flag_field_bits):
        '''Returns the flags set in a RAT header.'''

        flag_list = []

        for bit in range(0, 8):
            if flag_field_bits[bit] is "1":
                flag_list.append(RAT_FLAG_ORDER[bit])

        return flag_list

    def flag_set(self, flags):
        '''Returns a string corresponding to the given flags provided.'''

        output = ""
        for flag in RAT_FLAG_ORDER:
            if (flag in flags):
                output = output + "1"
            else:
                output = output + "0"

        return output

    def is_valid_flagmsg(self, flag_header, flag):
        '''Checks if the given flagged message contains the given flag.'''

        return "flags" in flag_header and flag \
             in self.flag_decode(flag_header["flags"])

    def zero_pad(self, num, length):
        '''Converts an input number into a binary number, and adds 
        leading zeros to num to pad it to given length.'''

        num = bin(int(num))[2:]
        padding = length - len(num)

        if (padding < 0):
            raise AssertionError(ERR_NUM_OUT_OF_RANGE)

        return bytes((padding * '0') + num, "utf-8")
        
    def construct_header(self, length, flags, offset):
        '''Constructs an 8-byte long RAT header.'''

        header = b""

        # Add stream_id
        header = header + self.zero_pad(self.stream_id, 16)

        # Add seq_num
        header = header + self.zero_pad(self.seq_num, 16)

        # Add length
        header = header + self.zero_pad(length, 16)

        # Add flags
        header = header + bytes(flags, "utf-8")

        # Add offset
        header = header + self.zero_pad(offset, 8)

        return header

    def data_decode(self, data, num_words):
        '''Returns a list of 16-bit numbers from a RAT payload.'''

        pass