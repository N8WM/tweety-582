"""Helper functions for the project"""

from irc.message import Message


def format_ws(message: Message) -> str:
    """Format a message"""
    assert message.content is not None
    return message.content.lower().strip(".!?").replace("'", "")
