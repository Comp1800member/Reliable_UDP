# Reliable_UDP
This program aims to facilitate reliable communication between a client and a server,
with a proxy server positioned in between to manage packet transfer by dropping or
delaying packets as needed.

The client and server will exchange packets that include sequence numbers,
acknowledgment (ack) numbers, and payloads. The sizes of each of these elements will
be calculated using a utilities (utils) file. After receiving a packet, both the client and
server will compute the appropriate sequence and acknowledgment numbers for their
responses (also calculated via the utils file) and send back a packet containing the
intended payload.

In the interim, the proxy server will control drop and delay rates, along with a specified
delay time. Upon receiving a packet, it will use its functions to determine whether to
drop it, delay it, or send it immediately.

Additionally, the proxy server will support dynamic updates to its drop rate, delay rate,
and delay-time values
