from argparse import ArgumentTypeError


def banner():
    """Print app banner"""
    # pylint: disable=W1401,C0303
    print(
        """
 _______ _______ _______    _______                                  _             
(_______|_______|_______)  (_______)                                | |            
   __    _  _  _ _    _     _       ___  ____  ____  _____ ____   __| |_____  ____ 
  / /   | ||_|| | |  | |   | |     / _ \|    \|    \(____ |  _ \ / _  | ___ |/ ___)
 / /____| |   | | |__| |   | |____| |_| | | | | | | / ___ | | | ( (_| | ____| |    
(_______)_|   |_|\______)   \______)___/|_|_|_|_|_|_\_____|_| |_|\____|_____)_|    
                                                                                   
"""
    )


def valid_port(port):
    """
    Determine the range of ports for ZMQ
    Used in argparse
    """
    port = int(port)
    if 1000 < port > 65535:
        raise ArgumentTypeError("Port must be between 1000 and 65535")
    return port
