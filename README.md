# Reliable UDP Communication Simulator

This project is a small UDP networking simulator designed to demonstrate reliable communication over an unreliable channel. It includes:

- a UDP server that receives packets and acknowledges them,
- a client that sends payloads and waits for acknowledgements,
- a middle proxy server that can drop or delay traffic,
- shared packet helper logic used to encode and decode packet fields.

The code is intended as a learning project for packet format design, reliable transmission concepts, and traffic manipulation in a controlled test environment.

## Project overview

The project simulates a simple request/response system where the client sends a message to the server through a proxy. The proxy can intentionally:

- drop packets,
- delay packets,
- forward packets normally,
- dynamically update drop/delay settings while running.

The server and client use a compact packet format with:

- packet size,
- sequence number,
- acknowledgement number,
- payload.

This format is defined in [utils.py](utils.py), and both sides use the same helpers to encode and parse it.

## Files in this repository

| File | Purpose |
| --- | --- |
| [server.py](server.py) | UDP server that receives packets and sends acknowledgements back to the sender. |
| [client.py](client.py) | Sends text messages to the server and waits for acknowledgements or timeouts. |
| [proxy_server.py](proxy_server.py) | Intercepts and forwards traffic, optionally dropping or delaying packets. |
| [utils.py](utils.py) | Packet encoding and parsing helpers, as well as packet constants. |
| [README.md](README.md) | Project documentation and usage guide. |

## How the communication works

### Packet format

The packet payload is encoded using this pattern:

`packet_size;sequence_number;acknowledgement_number;payload`

The packet size is calculated in [utils.py](utils.py), and the logic does the following:

- computes the acknowledgement number from the received sequence number and payload length,
- builds a binary-like packet structure in bytes,
- decodes the packet back into fields on receipt.

### Client side

The client:

1. connects to a target IP and port,
2. prompts for a message,
3. splits the message into payload-sized segments,
4. sends each segment with a sequence number,
5. waits for an acknowledgement,
6. retransmits on timeout or missing ACK up to a limit.

### Server side

The server:

1. binds to a specified IP and port,
2. waits for incoming UDP packets,
3. parses each packet,
4. prints the content,
5. generates a reply packet containing the acknowledgement information,
6. sends the packet back to the client.

### Proxy server

The proxy sits between the client and server. It receives traffic from both sides and can:

- drop packets by percentage,
- delay packets by percentage and a specific time range,
- forward packets onward when not dropped or delayed.

The proxy also supports runtime updates to the drop and delay values via interactive input.

## Installation

This project uses Python 3 and the `rich` package for styled terminal output.

Install the dependencies:

```bash
pip install rich numpy
```

If you do not need the proxy’s runtime interactive prompt, `rich` is still the important one for formatting output; `numpy` is imported in the proxy file and is expected to be present.

## Running the project

The typical flow is:

1. start the server,
2. start the proxy,
3. start the client,
4. type a message in the client terminal.

### 1) Start the server

```bash
python server.py --listen-ip 127.0.0.1 --listen-port 5000
```

This binds the server to localhost on port 5000.

### 2) Start the proxy server

```bash
python proxy_server.py \
  --listen-ip 127.0.0.1 \
  --listen-port 5001 \
  --target-ip 127.0.0.1 \
  --target-port 5000 \
  --client-drop 10 \
  --server-drop 5 \
  --client-delay 20 \
  --server-delay 10 \
  --client-delay-time 200 \
  --server-delay-time 50-150
```

The proxy listens on port 5001 and forwards traffic to the server at port 5000.

#### Proxy arguments

- `--listen-ip`: IP the proxy binds to
- `--listen-port`: port the proxy listens on
- `--target-ip`: destination server IP
- `--target-port`: destination server port
- `--client-drop`: drop probability for packets from the client to the server
- `--server-drop`: drop probability for packets from the server to the client
- `--client-delay`: delay probability for client traffic
- `--server-delay`: delay probability for server traffic
- `--client-delay-time`: delay time in milliseconds for client route, either a single value like `200` or a range like `50-150`
- `--server-delay-time`: delay time in milliseconds for server route, either a single value or a range

### 3) Start the client

```bash
python client.py --target-ip 127.0.0.1 --target-port 5001 --timeout 2
```

This tells the client to send messages to the proxy on port 5001. The proxy then relays them to the actual server at 5000.

#### Client arguments

- `-i`, `--target-ip`: IP of the server or proxy
- `-p`, `--target-port`: port of that target
- `-t`, `--timeout`: how long to wait for an acknowledgement before timing out

### 4) Send a message

Once the client starts, it will prompt:

```text
Message to send to the server (type 'exit' or ctrl+D to quit):
```

Type any message and press Enter.

Example:

```text
Hello from the UDP client!
```

The client will split the message into segments if needed, send them, and wait for acknowledgements.

## Example end-to-end flow

A sample local test sequence might look like this:

```bash
python server.py --listen-ip 127.0.0.1 --listen-port 5000
```

In another terminal:

```bash
python proxy_server.py --listen-ip 127.0.0.1 --listen-port 5001 --target-ip 127.0.0.1 --target-port 5000 --client-drop 0 --server-drop 0 --client-delay 0 --server-delay 0 --client-delay-time 0 --server-delay-time 0
```

In a third terminal:

```bash
python client.py --target-ip 127.0.0.1 --target-port 5001 --timeout 2
```

Then enter a message such as:

```text
Hello world
```

If everything is working, you will see packets being sent, received, acknowledged, and forwarded in the terminal output.

## Reliability behavior

The client implements a retry mechanism:

- packets are resent when no acknowledgement is received before timeout,
- a maximum retry count prevents infinite loops,
- duplicate acknowledgements are ignored to avoid handling repeated packets incorrectly.

This mirrors a basic reliability pattern used in transport protocols, although it is intentionally simplified for demonstration purposes.

## Proxy behavior notes

The proxy logic is designed to simulate an unreliable network path. It supports:

- random packet dropping,
- random packet delaying,
- explicit delay windows such as `50-150` milliseconds.

The proxy’s `update_drop_delay` method prompts for new values at runtime, but the actual execution flow is still driven by the command-line arguments and the main forwarding loop.

## Important notes

- This project uses UDP, not TCP.
- Packet delivery is not guaranteed by default; the proxy is intentionally simulating loss and delay.
- The code is best suited for local testing and demonstration rather than production-grade networking.
- For best results, run all three components on the same machine with loopback IPs such as `127.0.0.1`.

## Troubleshooting

### Client says timeout

Check that:

- the server is running,
- the proxy is running,
- the target port and IP match the actual service,
- the proxy and server are not bound to conflicting ports.

### Proxy does not forward traffic

Verify:

- the proxy listens on the port the client is targeting,
- the target IP and port point to the actual server,
- the server is accepting UDP traffic.

### Invalid port or IP

The scripts validate the input values and exit with a message if the port is outside the valid range or if the IP address is malformed.

## Summary

This project is a compact educational simulation of packet-based communication over an unreliable network. It demonstrates how sequence numbers, acknowledgements, packet loss, and delay can affect message delivery, while also showing a simple pattern for retransmission and forwarding.

You can use it to experiment with different drop and delay settings, observe how the reliability logic behaves, and better understand how protocols manage unreliable transport links.
