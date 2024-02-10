"""Contains IRC class for the bot"""

import random
import re
import socket
import time

from .constants import CHANNEL, NICKNAME, PORT, SERVER
from .message import Message


class IRC:
    """IRC class for the bot"""

    irc = socket.socket()

    def __init__(self, channel: str | None = None):
        """Initialize the IRC socket"""
        if channel:
            global CHANNEL
            CHANNEL = channel
        print("Initializing IRC socket...")
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.open = False

    def command(self, msg: str):
        """Send a command to the server"""
        if msg != "QUIT":
            print(f"  > {msg}")
        self.irc.send(bytes(msg + "\n", "UTF-8"))

    def send(self, message: Message):
        """Send a message to the channel"""
        if self.open:
            time.sleep(random.randint(1, 3))
            self.command(f"PRIVMSG {CHANNEL} :{message.assemble()}")

    def connect(self):
        """Connect to the server"""
        print(f'Connecting to "{CHANNEL}" through "{SERVER}:{PORT}"...')
        self.irc.connect((SERVER, PORT))
        self.open = True
        print("Connected\n")

        # Perform user authentication
        self.command("USER " + NICKNAME + " " + NICKNAME + " " + NICKNAME + " :python")
        self.command("NICK " + NICKNAME)
        time.sleep(5)

        # join the channel
        self.command("JOIN " + CHANNEL)

    def disconnect(self):
        """Disconnect from the server"""
        print("\nDisconnecting...")
        self.command("QUIT")
        self.open = False
        print("Disconnected")

    def get_response(self) -> list[Message]:
        """Get the response from the server"""
        time.sleep(1)
        resp = self.irc.recv(2040).decode("UTF-8").lstrip()
        raw_messages = re.findall(r"(:.*?)(?=:\n|$)", resp, re.DOTALL | re.MULTILINE)
        split_messages = [m.replace("\n", "") for m in raw_messages]
        messages = [Message(m) for m in split_messages if m]

        if resp.find("PING") != -1:
            self.command("PONG " + resp.split()[1] + "\r")

        error_queue = []

        for message in messages:
            if message.error:
                error_queue.append(message.error)
                self.open = False

        if len(error_queue) > 0:
            for message in messages:
                print(f"  < {message.raw_message}")
            print("\nError:", "\n       ".join(error_queue))
            print("Disconnected")
            return []

        return messages

    def messages(self):
        """Get messages from the server"""
        while self.open:
            for message in self.get_response():
                if not self.open:
                    break
                if message.is_for_bot():
                    print(f"* < {message.raw_message}")
                    yield message
                elif message.is_priv():
                    print(f"  < {message.raw_message}")
                    yield message
                else:
                    print(f"  $ {message.raw_message}")
