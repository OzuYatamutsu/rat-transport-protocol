# rat-transport-protocol
The Reliable As TCP (RAT) protocol is a connection-oriented transport-layer extension on top of UDP that extends UDP to provide a similar level of reliability as TCP. Like TCP, it supports window-based flow control and byte-stream semantics, but focuses on implementing reliability as simply as possible.

#### Answers to common questions
Included below are short answers to common questions regarding reliable transport, which will be expanded in further detail later in the specification.
##### Non-pipelined or pipelined?
RAT is a **pipelined** protocol, and employs _selective repeat_ to handle retransmission of lost segments.
##### Lost packets?
RAT handles retransmission by the use of `ACK` and `NACK` overhead messages, where the protocol will alert the sender of each segment which was not received. The sequence numbers themselves will be sent in a single `NACK` message if possible, or in as few messages as possible - either way as part of the message payload.
##### Corrupted packets?
RAT includes multiple methods of detecting packet corruption:
 * **A unique stream ID** assigned by the server to a client, which must match on both ends
 * **A single sequence number**
 * **A simple checksum** of a set of message flag fields
 * **UDP's checksum**, as RAT is built on top of UDP

##### Duplicate packets?
If a segment is received with a sequence number which has already passed, the segment is discarded.
##### Out-of-order packets?
RAT segments include a _sequence number_, which tracks the order that they were sent from a sender (and the order they should be reassembled).
##### Bi-directional data transfer?
All RAT streams are _uni-directional_ at any given point in time. Client and servers can send and receive on a single stream, but these operations cannot occur at the same time. However, additional connections can be opened (with different stream IDs) which can allow for bi-directional data transfer in parallel.
## Header
The full RAT header is 2 bytes wide, and is built on top of a UDP datagram:
<IMG1 HERE>
#### Stream ID
The stream ID is temporally unique **32-bit** identifier used to uniquely identify an active data stream at any moment in time. Stream IDs are *server-significant*, and are assigned and used by the server to uniquely identify a connection stream to a specific client. In the initial connection from client to server, this value is set to 0 by the client until the server assigns one.
#### Sequence number
A sequence number is an **16-bit** number that identifies the current segment in a RAT connection stream.
#### Flags
The flags field is a **7-bit** series of flag bits which identify specific RAT overhead message types. Field bits are specified in order below, and are also generally ordered from most-to-least used.

Field bits may also include additional overhead data in the payload - the amount of additional overhead data carried, in bytes, is specified in the data offset header. If field bits do not require additional overhead data, they can be set along with data streams.
##### ACK
If this bit is set, this message is an acknowledgement that a message or series of messages were receieved successfully.
##### NACK
If this bit is set, this message is an acknowledgement that a message in a window was never recieved.
##### SWIN
If this bit is set, this message includes a request to change the current window size.
##### RST
If this bit is set, this message identifies that the next sequence number will start again at 0.
##### ALI
If this bit is set, this message is a RAT keep-alive message, signaling to the server to keep this connection active. A keep-alive message can be acknowledged by the server (by replying with a message with the `ACK` and `ALI` flags set) or ignored.
##### HLO
If this bit is set, this message is a request to connect a client to a server.
##### BYE
If this bit is set, this message is a request to disconnect a client from a server.

#### Data offset
This is an **6-bit** value which specifies the amount of additional **16-byte words** of overhead this RAT segment needs to store in the payload relating to one or more set flags. In general, if this value is anything other than 0, the RAT message data is carried in lieu of a data payload.

Some examples of this additional data are:

 * **NACK**: A list of sequence numbers that were not receieved during the current window. The server will resend those specific segments along with new segments as part of the next window.

 * **SWIN**: An 16-bit number that specifies the new requested window size.

#### Flag checksum
A field that simply stores the sum of the flags and data offset fields as a \textbf{3-bit unsigned integer} (overflow is expected). If the value in this field does not match the 3-bit sum of the fields, an error is detected and the segment is discarded.

#### UDP header
Other methods and values (such as service selection, payload length, and UDP checksum) are handled by the underlying UDP header:

##### Source port
The source port is a **16-bit** value (0-65535) which identifies the source communication endpoint for a RAT connection stream. A port number is used to identify a service running on a server, or used to identify a connection stream on a client.

##### Destination port
The destination port is a **16-bit** value (0-65535) which identifies the destination communication endpoint for a RAT connection stream. A port number is used to identify a service running on a server, or used to identify a connection stream on a client.

##### Length
The length field is a **16-bit** field that specifies the total length, in bytes, of the UDP header and payload.

##### Checksum
The checksum field is a **16-bit** field that is used for error-checking of the UDP header and payload.

## Methods
A RAT API implementation must implement the following methods:

### Server
#### `listen(address, port, num_connections)`
Listens for a maximum of `numconnections` connections on `port` at address `port`. This allocates space for a connection queue, and new connections on this socket will be placed in this queue.
#### `accept()`
Accepts a connection from a connection queue and returns a new client socket to use. This removes the connection from the connection queue. If there are no connections in the queue, this is a blocking I/O call, and the program will sleep until a connection is available to accept. The client socket will have an established connection to the client.
#### `allow_keepalives(bool)`
Directs the socket to follow or ignore keep-alive messages. The default is to allow keep-alives. This setting can be set on individual client sockets returned from \texttt{accept()}, or for all clients on a server socket by setting it on the server socket instead.

### Client
#### `connect(address, port, send_keepalives)`
Attempts to connect to a server socket on port `port` at address `address`. If successful, the current socket will have an established connection to the server. An optional keep-alive directive can be set - this specifies that the client should send keep-alive messages from client to server after the last ACK message was received, while a connection is still established. A keep-alive message is a request to keep a socket open when no data is currently being sent. The default value is *false* (don’t send keep-alives), and a server can choose to ignore keep-alive messages if desired.

### Server and client
#### `send(bytes)`
Sends a byte-stream from client to server or from server to client.
#### `recv(buffer_size)`
Returns the byte-stream result of reading `buffer_size` bytes from an established socket.
#### `close()`
Attempts to cleanly close a socket and shut down the connection stream. Sockets which are closed should be discarded, as they cannot be reopened.
## State
The RAT connection stream timeline can be separated into two distinct stages: connection establishment and connection closing.
### Connection establishment
#### `SOCK_UNOPENED`
The initial state following the creation of a socket on the client or server. Unopened sockets do not have any connection or addressing information, and cannot be used to send data until it is opened by a call to `connect(address, port, keepalive_time)` on the client or `listen(address, port, num_connections)` on the server.
#### `SOCK_SERVOPEN`
The state on the server following a call to `listen(address, port, num_connections)` on the server. This server is currently listening for connections.
#### `SOCK_HLOSENT`
The state on the client following a call to `connect(address, port, keepalive_time)` on the client. This client has opened its socket, and has sent a `HLO` message to the server to attempt to establish a connection.
#### `SOCK_HLORECV`
The state on the server after its opened socket has received a `HLO` message from a client. This server will respond with a `ACK, HLO` message, containing a unique stream ID assigned to the client by this server.
#### `SOCK_ESTABLISHED`
The state on the client after receiving a `ACK, HLO` message from the server, and the state on the server following an `ACK` reply to the `ACK, HLO` sent from the client to the server, containing the client’s unique stream ID. This socket is now ready to send data. If a keep-alive directive was specified on the client when it initially opened its socket, the client will attempt to remain in this state until it sends or receives any message, including keep-alives.
### Connection closing
#### `SOCK_BYESENT`
The state on the client or server following a call to `close()`. This call places the socket in a *half-open* state, where the client or server can no longer send data, but can continue to receive data from the server and send `ACK` responses. This starts the `RAT_BYE_TIMEOUT` timer, which counts down from the receipt of the last RAT segment - the client or server will remain in this state until either the server acknowledges the connection close with a `ACK, BYE` message, or `RAT_BYE_TIMEOUT` expires.
#### `SOCK_BYERECV`
The state on the client or server after its socket has received a `BYE` message from the other end on an established socket. The client or server will continue to send data to complete its current window, and will send a `ACK, BYE` message upon receiving the last `ACK` from the other end at the conclusion of the final window. Once sent, this starts the `RAT_BYE_TIMEOUT` timer, after which the socket transitions to the `SOCK_CLOSED` state.
#### `SOCK_CLOSED`
The state on the client or server following an `ACK, BYE` response from the server or the expiration of a `RAT_BYE_TIMEOUT` timer. This socket is closed and cannot be used to send data or re-establish a connection and should be deallocated from memory.
### Timers
RAT maintains two main timers to handle cases where it does not receive an expected response from the other side. The exact values of these timers are based on how the RAT protocol is implemented on the client or server.
#### `RAT_REPLY_TIMEOUT`
A timer started after the receipt of the last message. This timer resets when any message is received (such as data or keep-alive messages). When it expires, the socket transitions immediately to the `SOCK_CLOSED` state.
#### `RAT_BYE_TIMEOUT`
A timer started after the receipt of the last message in the `SOCK_BYESENT` or `SOCK_BYERECV` states (which can include a `BYE` message itself). This should be less than the `RAT_REPLY_TIMEOUT` timer. When it expires, the socket transitions immediately to the `SOCK_CLOSED` state.
