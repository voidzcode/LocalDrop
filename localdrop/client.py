import socket
from pathlib import Path

from .protocol import receive_json, send_json


PORT = 5000


def send_file(host, filepath):
    filepath = Path(filepath)

    if not filepath.exists():
        print("File does not exist.")
        return

    if not filepath.is_file():
        print("That path is not a file.")
        return

    filesize = filepath.stat().st_size

    print(f"Connecting to {host}:{PORT}...")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((host, PORT))

        send_json(client, {
            "type": "file",
            "filename": filepath.name,
            "filesize": filesize
        })

        response = receive_json(client)

        if not response or response.get("type") != "ready":
            print("Receiver rejected the transfer.")
            return

        print(f"Sending: {filepath.name}")
        print(f"Size: {filesize:,} bytes")

        sent = 0

        with open(filepath, "rb") as file:
            while True:
                chunk = file.read(1024 * 1024)

                if not chunk:
                    break

                client.sendall(chunk)
                sent += len(chunk)

                percentage = (sent / filesize) * 100

                print(
                    f"\rProgress: {percentage:6.2f}%",
                    end="",
                    flush=True
                )

        print()

        response = receive_json(client)

        if response and response.get("type") == "complete":
            print("Transfer complete!")

    except ConnectionRefusedError:
        print("Could not connect to the receiver.")
        print("Make sure LocalDrop is running on the other computer.")

    except ConnectionError as error:
        print(f"Connection error: {error}")

    finally:
        client.close()