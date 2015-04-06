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
