import socket
from pathlib import Path

from .protocol import receive_json, send_json


HOST = "0.0.0.0"
PORT = 5000

DOWNLOAD_FOLDER = Path("received_files")


def start_server():
    DOWNLOAD_FOLDER.mkdir(exist_ok=True)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen(5)

    print(f"LocalDrop receiver running on port {PORT}")
    print(f"Files will be saved to: {DOWNLOAD_FOLDER.absolute()}")
    print()

    while True:
        client, address = server.accept()

        print(f"Connection from {address[0]}")

        try:
            receive_file(client)
        except Exception as error:
            print(f"Transfer failed: {error}")
        finally:
            client.close()


def receive_file(client):
    info = receive_json(client)

    if not info:
        return

    if info.get("type") != "file":
        raise ValueError("Invalid transfer request.")

    filename = Path(info["filename"]).name
    filesize = int(info["filesize"])

    destination = DOWNLOAD_FOLDER / filename

    # Prevent accidentally overwriting an existing file.
    counter = 1

    while destination.exists():
        destination = (
            DOWNLOAD_FOLDER
            / f"{Path(filename).stem}_{counter}{Path(filename).suffix}"
        )
        counter += 1

    print(f"Receiving: {filename}")
    print(f"Size: {filesize:,} bytes")

    send_json(client, {
        "type": "ready"
    })

    received = 0

    with open(destination, "wb") as file:
        while received < filesize:
            chunk = client.recv(min(1024 * 1024, filesize - received))

            if not chunk:
                raise ConnectionError("Sender disconnected.")

            file.write(chunk)
            received += len(chunk)

            percentage = (received / filesize) * 100

            print(
                f"\rProgress: {percentage:6.2f}%",
                end="",
                flush=True
            )

    print()
    print(f"Saved to: {destination}")

    send_json(client, {
        "type": "complete"
    })