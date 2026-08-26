import argparse
import time

from localdrop.client import send_file
from localdrop.discovery import Discovery
from localdrop.server import start_server


def main():
    parser = argparse.ArgumentParser(
        description="LocalDrop - local network file transfer"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    receive_parser = subparsers.add_parser(
        "receive",
        help="Start the receiver"
    )

    receive_parser.add_argument(
        "--name",
        default="LocalDrop Device",
        help="Device name"
    )

    send_parser = subparsers.add_parser(
        "send",
        help="Send a file"
    )

    send_parser.add_argument(
        "host",
        help="IP address"
    )

    send_parser.add_argument(
        "file",
        help="File to send"
    )

    discover_parser = subparsers.add_parser(
        "discover",
        help="Find LocalDrop devices"
    )

    discover_parser.add_argument(
        "--name",
        default="LocalDrop Device",
        help="Your device name"
    )

    args = parser.parse_args()

    if args.command == "receive":
        discovery = Discovery(args.name)
        discovery.start()

        print("Waiting for files...")
        start_server()

    elif args.command == "send":
        send_file(args.host, args.file)

    elif args.command == "discover":
        discovery = Discovery(args.name)
        discovery.start()

        print("Searching for LocalDrop devices...")
        print("Press Ctrl+C to stop.\n")

        try:
            while True:
                devices = discovery.get_devices()

                print("\033[2J\033[H", end="")

                print("LocalDrop Devices")
                print("=================\n")

                if not devices:
                    print("No devices found.")

                for device in devices:
                    print(
                        f"🖥️  {device['name']}"
                    )
                    print(
                        f"   IP: {device['ip']}"
                    )
                    print(
                        f"   Port: {device['port']}\n"
                    )

                time.sleep(1)

        except KeyboardInterrupt:
            discovery.stop()
            print("\nDiscovery stopped.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()