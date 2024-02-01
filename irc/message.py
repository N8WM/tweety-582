"""Contains message class for IRC messages"""

import re
from .constants import CHANNEL, NICKNAME


class Message:
    """Message class for IRC messages"""
    def __init__(
        self,
        raw_message: str | None = None,
        target: str | None = None,
        content: str | None = None,
    ) -> None:
        assert (
            raw_message is not None or content is not None
        ), "Message Error: either raw_message or content must be specified"
        self.error = None
        if raw_message:
            self.raw_message = raw_message
            self.parse()
        else:
            self.target = target
            self.content = content

    def is_for_bot(self) -> bool:
        """Check if the message is for the bot"""
        if self.raw_message is None:
            return False
        v_command = "PRIVMSG" in self.raw_message
        v_channel = CHANNEL in self.raw_message
        v_target = self.target == NICKNAME
        return v_command and v_channel and v_target

    def parse(self) -> None:
        """Parse the raw message (internal use only)"""
        tstart = self.raw_message.find(":", 1) + 1
        text = self.raw_message[tstart:]
        cstart = text.find(":") + 1
        if re.match(r"^[^\s:]+:.*$", text):
            self.target = text[: cstart - 1]
        else:
            cstart = 0
            self.target = None
        self.content = text[cstart:].lstrip()
        if not "PRIVMSG" in self.raw_message and "ERROR" in self.raw_message:
            self.error = "something broke"
            error_sp = self.raw_message.split(":")
            if len(error_sp) > 2:
                self.error = error_sp[1]

    def assemble(self) -> str:
        """Assemble the message"""
        assert self.content is not None, "Message Error: content must be specified"
        target_str = "" if self.target is None else (self.target + ": ")
        return target_str + self.content
