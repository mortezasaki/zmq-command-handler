import argparse
import logging
import os
import sys
from typing import List, Union

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

from core.config import settings
from core.serialize import SerializingContext
from models.command import CommandResult, MathCommand, OSCommand
from utils.functions import banner, valid_port


def get_options(argv: List[str]) -> argparse.Namespace:
    """Get options from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=valid_port, default=settings.PORT, help="port number")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    options = parser.parse_args(argv)
    return options


def connect(port: int) -> zmq.Socket:
    """Initialize zmq server"""
    context = SerializingContext()

    # Start an authenticator for this context.
    auth = ThreadAuthenticator(context)
    auth.start()
    auth.allow("127.0.0.1")
    # Tell authenticator to use the certificate in a directory
    auth.configure_curve(domain="*", location=str(settings.PUBLIC_KEYS_DIR))

    socket = context.socket(zmq.REP)  # pylint: disable=no-member
    server_secret_file = os.path.join(settings.SECRET_KEYS_DIR, "server.key_secret")
    server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
    socket.curve_secretkey = server_secret
    socket.curve_publickey = server_public
    socket.curve_server = True  # must come before bind
    try:
        socket.bind(f"tcp://*:{port}")
    except zmq.ZMQError:
        logging.info("Could not bind to port. Use another port")
        sys.exit(1)
    return socket


ClientCommands = List[Union[OSCommand, MathCommand]]


def listen(socket: zmq.Socket) -> ClientCommands:
    """Listen for new client commands"""
    return socket.recv_zipped_pickle()


def execute_commands(commands: ClientCommands) -> CommandResult:
    """Execute a list of commands"""
    responses = []
    for cmd in commands:
        try:
            logging.info("Run '%s' command...", cmd.command)
            responses.append(cmd.run())
            logging.info("'%s' has been successfully executed", cmd.command)
        except AttributeError:  # Invalid type of command from a client
            logging.info("'%s' cannot be handled by the server.", cmd.command)
    return responses


def main(argv: List[str] = sys.argv[1:]) -> None:  # pylint: disable=dangerous-default-value
    """Set up a ZMQ server, listen for client commands, and reply to them."""

    options = get_options(argv)

    if options.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level, format="[%(asctime)s] [%(levelname)s] %(message)s")

    logging.info("Starting ZMQ server...")
    socket = connect(options.port)
    try:
        while True:
            logging.info("Listening at: tcp://*:%d", options.port)
            commands = listen(socket)
            logging.info("Client-side commands are received...")
            responses = execute_commands(commands)
            logging.info("Send responses to the client...")
            socket.send_zipped_pickle(responses)
    except KeyboardInterrupt:
        logging.info("Interrupted by user")


if __name__ == "__main__":
    banner()
    main()
