import socket

HOST = "128.178.128.16"
PORT = 56765

# magical byte string which opens a TCP connection
handshake = \
    b"\x00\x00\x00\x1a"\
    b"\x54\x50\x76\x31"\
    b"\x00\x01\x84\x01"\
    b"\x00\x00\x00\x00"\
    b"\x00\x01\x52\x00"\
    b"\x00\x00\x00\x00\x00\x00"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # connect to the port
    s.connect((HOST, PORT))

    # send handshake message
    s.send(handshake)
    # receive handshake response message which we can’t parse
    _ = s.recv(1024)

    # The connection should now be open
    ...
