# ZMQ Command Handler

A server-client application that executes commands over ZMQ with Curve encryption
## Installation

Create a virtual environment and activate it by running the following commands:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the necessary packages with the following command:
```bash
pip install -r requirements.txt
```

Run the following command if a new certificate is required:
```bash
python generate_certificates.py
```

## Usage
### Server
```bash
python server.py
```

### Client
```bash
python client.py --file "samples/commands.js"
```