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
