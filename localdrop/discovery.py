import json
import socket
import threading
import time


DISCOVERY_PORT = 5001
TRANSFER_PORT = 5000
BROADCAST_INTERVAL = 3


class Discovery:
    def __init__(self, device_name):
        self.device_name = device_name
        self.running = False
        self.devices = {}
        self.thread = None

    def start(self):
        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._listen,
            daemon=True
        )

        self.thread.start()

        threading.Thread(
            target=self._broadcast,
            daemon=True
        ).start()

        print(f"Discovery started as '{self.device_name}'")

    def stop(self):
        self.running = False

    def _broadcast(self):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            1
        )

        message = json.dumps({
            "type": "localdrop_discovery",
            "name": self.device_name,
            "port": TRANSFER_PORT
        }).encode("utf-8")

        while self.running:
            try:
                sock.sendto(
                    message,
                    ("<broadcast>", DISCOVERY_PORT)
                )
            except OSError:
                pass

            time.sleep(BROADCAST_INTERVAL)

        sock.close()

    def _listen(self):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        sock.bind(("", DISCOVERY_PORT))

        sock.settimeout(1)

        while self.running:
            try:
                data, address = sock.recvfrom(4096)

                message = json.loads(
                    data.decode("utf-8")
                )

                if message.get("type") != "localdrop_discovery":
                    continue

                ip = address[0]

                # Don't add ourselves.
                if ip == self.get_local_ip():
                    continue

                self.devices[ip] = {
                    "name": message.get("name", "Unknown"),
                    "ip": ip,
                    "port": message.get(
                        "port",
                        TRANSFER_PORT
                    ),
                    "last_seen": time.time()
                }

            except socket.timeout:
                continue

            except (OSError, json.JSONDecodeError):
                continue

        sock.close()

    def get_devices(self):
        current_time = time.time()

        # Remove devices that haven't
        # announced themselves for 10 seconds.
        expired = [
            ip
            for ip, device in self.devices.items()
            if current_time - device["last_seen"] > 10
        ]

        for ip in expired:
            del self.devices[ip]

        return list(self.devices.values())

    @staticmethod
    def get_local_ip():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
        except OSError:
            ip = "127.0.0.1"
        finally:
            sock.close()

        return ip