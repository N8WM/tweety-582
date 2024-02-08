"""Contains Tweety Bot class for IRC"""

import random

from irc.irc import IRC
from irc.message import Message
from music.music import MusicHandler, SongInfo

from .commands.commands import Command, CommandHandler


class TweetyBot:
    """Tweety Bot class for IRC"""

    def __init__(self):
        self.irc = IRC()
        self.ch = CommandHandler()
        self.mh = MusicHandler()

        self.ch.add_command(
            Command(  # Hello
                phrases=["hello", "hi", "hey", "whats up"], callback=self.hello
            )
        )

        self.ch.add_command(
            Command(  # Title of song
                phrases=[
                    "song name",
                    "What song was that?",
                    "What is that song called?",
                ],
                callback=self.song_title,
            )
        )

        self.ch.add_command(
            Command(  # Artist of song
                phrases=[
                    "song artist",
                    "who",
                    "who sang",
                    "Who sings that song?",
                    "Who made that song?",
                ],
                callback=self.song_artist,
            )
        )

        self.ch.add_command(
            Command(  # Year of song
                phrases=[
                    "song year",
                    "when",
                    "song release date",
                    "When was that song made?",
                ],
                callback=self.song_year,
            )
        )

        self.ch.add_command(
            Command(  # Genre of song
                phrases=["song genre", "What genre is that song?"],
                callback=self.song_genre,
            )
        )

        self.ch.add_command(
            Command(phrases=["die"], callback=self.die, exact=True)  # Die
        )

    def start(self):
        """Start the bot"""
        self.irc.connect()

        try:
            for message in self.irc.messages():
                self.ch.new_message(message)

                if message.is_for_bot():
                    command = self.ch.closest_command(threshold=0.2, min_diff=0.1)

                    if command is not None:
                        print(
                            f"\n[Matched phrase: {command.get_last_matched_phrase()}]\n"
                        )
                        response = command.run(command)
                        assert isinstance(response, Message)
                        self.irc.send(response)
                else:
                    stanza = self.mh.next_stanza(message)
                    if stanza is not None:
                        rhetorical_type = random.choice(list(SongInfo))

                        # likelihood to ask rhetorical
                        ask_rhetorical = random.random() <= 0.3

                        self.ch.new_stanza(
                            stanza, rhetorical_type if ask_rhetorical else None
                        )

        except KeyboardInterrupt:
            self.irc.send(Message(content="i have been terminated X.X"))
            self.irc.disconnect()

    ### COMMANDS ###

    def hello(self, _: Command) -> Message:
        """Hello command"""
        latest_message = self.ch.context.latest_message
        assert latest_message is not None

        return Message(
            target=latest_message.sender,
            content=random.choice(["hey!", "heya!", "heyyyy :3", "^.^", "yooo"]),
        )

    def song_title(self, command: Command) -> Message:
        """Song name command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None

        if cur_stanza is None:
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        response = Message(
            target=latest_message.sender, content=f'it\'s called "{cur_stanza.title}"'
        )

        if context.cur_rhet is SongInfo.SONG_TITLE:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3"
                )
        elif command.already_ran:
            response.content = (
                "i already answered that haha but that's okay, "
                + f'it\'s called "{cur_stanza.title}"'
            )
        else:
            command.already_ran = True

        return response

    def song_artist(self, command: Command) -> Message:
        """Song artist command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None

        if cur_stanza is None:
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        response = Message(
            target=latest_message.sender, content=f"it's by {cur_stanza.artist}"
        )

        if context.cur_rhet is SongInfo.SONG_ARTIST:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3"
                )
        elif command.already_ran:
            response.content = (
                "i already answered that haha but that's okay, "
                + f"it's by {cur_stanza.artist}"
            )
        else:
            command.already_ran = True

        return response

    def song_year(self, command: Command) -> Message:
        """Song year command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None

        if cur_stanza is None:
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        response = Message(
            target=latest_message.sender,
            content=f"it was released in {cur_stanza.year}",
        )

        if context.cur_rhet is SongInfo.SONG_YEAR:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3"
                )
        elif command.already_ran:
            response.content = (
                "i already answered that haha but that's okay, "
                + f"it was released in {cur_stanza.year}"
            )
        else:
            command.already_ran = True

        return response

    def song_genre(self, command: Command) -> Message:
        """Song genre command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None

        if cur_stanza is None:
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        response = Message(
            target=latest_message.sender, content=f"it's a {cur_stanza.genre} song"
        )

        if context.cur_rhet is SongInfo.SONG_GENRE:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3"
                )
        elif command.already_ran:
            response.content = (
                "i already answered that haha but that's okay, "
                + f"it's a {cur_stanza.genre} song"
            )
        else:
            command.already_ran = True

        return response

    def die(self, _: Command) -> Message:
        """Die command"""
        latest_message = self.ch.context.latest_message
        assert latest_message is not None

        return Message(target=latest_message.sender, content="aww okay, goodbye... X.X")
