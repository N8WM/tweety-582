"""Helper functions for the project"""

import re
from irc.message import Message


def simplify(message: Message) -> str:
    """Format a message to make it easier to compare"""
    assert message.content is not None
    return re.sub(r"\.|!|\?|'|,", r"", message.content.lower()).strip()
