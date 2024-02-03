"""Contains Tweety Bot class for IRC"""

import random

from irc import IRC, Message

from .helpers import simplify


class TweetyBot:
    """Tweety Bot class for IRC"""

    def __init__(self):
        self.irc = IRC()
        self.commands = [self.hello, self.die]
        self.current_message: Message | None = None
        self.commands_run: list[str] = []
        self.last_song_id: str | None = None

    def start(self):
        """Start the bot"""
        self.irc.connect()

        try:
            for message in self.irc.messages():
                self.commands_run = []
                self.current_message = message
                for command in self.commands:
                    command()

                if len(self.commands_run) == 0:
                    self.irc.send(Message(content=message.content))

        except KeyboardInterrupt:
            self.irc.send(Message(content="I have been terminated X.X"))
            self.irc.disconnect()

    ## ===  Commands === ##

    def hello(self):
        """Hello command"""
        if len(self.commands_run) > 0:
            return

        assert self.current_message is not None

        run_ = simplify(self.current_message) in {
            "hi",
            "hey",
            "hello",
            "howdy",
            "greetings",
            "whats up",
            "hows it going",
            "long time no see",
        }

        if run_:
            responses = ["Hey!", "Heya!", "Heyyyy :3", "^.^", "Yooo"]
            self.irc.send(Message(content=random.choice(responses)))
            self.commands_run.append("hello")

    def die(self):
        """Die command"""
        if len(self.commands_run) > 0:
            return

        assert self.current_message is not None

        run_ = simplify(self.current_message) in {"die"}

        if run_:
            self.irc.send(Message(content="Aww okay, goodbye... X.X"))
            self.irc.disconnect()
            self.commands_run.append("die")
