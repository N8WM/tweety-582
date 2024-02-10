"""Constants for IRC"""

CHANNEL = "#CSC582"
SERVER = "irc.libera.chat"
PORT = 6667
NICKNAME = "Tweety-bot"

def update_channel(channel: str) -> None:
    """Update the channel"""
    global CHANNEL
    CHANNEL = channel
