import argparse
import logging
import os
import sys
from json import load as load_json
from json.decoder import JSONDecodeError
from time import sleep
from typing import List

import zmq
import zmq.auth

from core.config import settings
from core.serialize import SerializingContext
from models.command import MathCommand, OSCommand
from utils.functions import banner, valid_port


def get_options(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port", type=valid_port, default=5560, help="port number"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="host address",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="samples/commands.json",
        help="path to json file",
    )
    options = parser.parse_args(argv)
    return options


def connect(host, port):
    context = SerializingContext()
    socket = context.socket(zmq.REQ)  # pylint: disable=no-member
    # We need two certificates, one for the client and one for
    # the server. The client must know the server's public key
    # to make a CURVE connection.
    client_secret_file = os.path.join(settings.SECRET_KEYS_DIR, "client.key_secret")
    client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
    socket.curve_secretkey = client_secret
    socket.curve_publickey = client_public

    server_public_file = os.path.join(settings.PUBLIC_KEYS_DIR, "server.key")
    server_public, _ = zmq.auth.load_certificate(server_public_file)
    # The client must know the server's publ
    socket.curve_serverkey = server_public
    socket.connect(f"tcp://{host}:{port}")
    return socket


def parse_json(json_file):
    if not os.path.exists(json_file):
        raise FileNotFoundError("Json file does not exist.")
    with open(json_file, "r", encoding="utf-8") as commands_file:
        try:
            json_data = load_json(commands_file)
        except JSONDecodeError as json_error:
            raise ValueError("Invalid json file") from json_error

    commands = []

    # Use of structural pattern matching in Python 3.10 or higher
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 10:
        pass
        ## Black formatter can't parse match
        ## This section has been commented because of this reason

        # for data in json_data:
        #     # fmt: off
        #     match data:
        #     # fmt: on
        #         case {"command_type": "os"}:
        #             os_coommand = OSCommand(data["command_name"], data["parameters"])
        #             commands.append(os_coommand)
        #         case {"command_type": "compute"}:
        #             math_coommand = MathCommand(command=data["expersion"])
        #             commands.append(math_coommand)
        #         case _:
        #             raise ValueError("Invalid command type")
    else:
        for data in json_data:
            if data["command_type"] == "os":
                os_coommand = OSCommand(data["command_name"], data["parameters"])
                commands.append(os_coommand)
            elif data["command_type"] == "compute":
                math_coommand = MathCommand(command=data["expersion"])
                commands.append(math_coommand)
            else:
                raise ValueError("Invalid command type")

    return commands


def send_data(socket, json_file):
    parsed_commands = parse_json(json_file)
    socket.send_zipped_pickle(parsed_commands)


def get_response(socket):
    response = socket.recv_zipped_pickle()
    return response


def main(
    argv: List[str] = sys.argv[1:],
) -> None:  # pylint: disable=dangerous-default-value
    """Client main function."""
    options = get_options(argv)

    if options.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level, format="[%(asctime)s] [%(levelname)s] %(message)s")

    logging.info("Starting ZMQ client...")
    logging.info("Connecting to: tcp://%s:%d", options.host, options.port)
    socket = connect(options.host, options.port)
    logging.info("Send commands to: tcp://%s:%d", options.host, options.port)
    send_data(socket, options.file)
    logging.info("Waiting for response from: tcp://%s:%d", options.host, options.port)
    sleep(1)
    for resp in get_response(socket):
        print("=" * 100, "\n", resp)

    print("\n", "/" * 100, "\n\n")

    logging.info("Results were successfully received.")


if __name__ == "__main__":
    banner()
    main()
