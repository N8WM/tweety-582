"""Contains message class for IRC messages"""

import re

from irc import constants as c


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
        self.sender = None
        if raw_message:
            self.raw_message = raw_message
            self.parse()
        else:
            self.target = target
            self.content = content

    def is_priv(self) -> bool:
        """Check if the message is a private message"""
        if self.raw_message is None:
            return False
        v_command = "PRIVMSG" in self.raw_message
        v_channel = c.CHANNEL in self.raw_message
        v_sender = self.sender is not None
        return v_command and v_channel and v_sender

    def is_for_bot(self) -> bool:
        """Check if the message is for the bot"""
        if self.raw_message is None:
            return False
        v_target = self.target == c.NICKNAME
        return self.is_priv() and v_target

    def parse(self) -> None:
        """Parse the raw message (internal use only)"""
        error_match = re.match(r"^ERROR(?:\s*:(?P<content>.*))?$", self.raw_message)
        if error_match is not None:
            self.error = error_match.group("content")
            self.error = self.error if self.error else "something broke"
            return

        sender_match = re.match(r"^:([A-Za-z0-9-_@&$()/]+)!.*$", self.raw_message)
        main_match = re.search(
            rf".*PRIVMSG {c.CHANNEL} :(?:(?P<target>[^\s]+):\s*)?(?P<content>.*)\s*$",
            self.raw_message,
        )

        self.sender = sender_match.group(1) if sender_match else None
        self.target = main_match.group("target") if main_match else None
        self.content = main_match.group("content") if main_match else None

    def assemble(self) -> str:
        """Assemble the message"""
        assert self.content is not None, "Message Error: content must be specified"
        target_str = "" if self.target is None else (self.target + ": ")
        return target_str + self.content
