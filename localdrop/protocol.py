import json
import struct


def send_json(sock, data):
    message = json.dumps(data).encode("utf-8")
    header = struct.pack("!I", len(message))

    sock.sendall(header)
    sock.sendall(message)


def receive_json(sock):
    header = receive_exact(sock, 4)

    if not header:
        return None

    message_length = struct.unpack("!I", header)[0]
    message = receive_exact(sock, message_length)

    return json.loads(message.decode("utf-8"))


def receive_exact(sock, size):
    data = bytearray()

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            raise ConnectionError("Connection closed unexpectedly.")

        data.extend(chunk)

    return bytes(data)