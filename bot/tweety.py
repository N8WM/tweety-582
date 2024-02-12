"""Contains Tweety Bot class for IRC"""

import random

from bot.commands import helpers
from irc.irc import IRC
from irc.message import Message
from music.music import MusicHandler, SongInfo

from .commands.commands import Command, CommandHandler


def oxford(items: list[str]) -> str:
    """
    Join a list of strings together with commas, with an
    "and" at the end
    """
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


class PersonMemory:
    """Memory of a specific person"""

    greet = "we greeted eachother"
    purpose = "you asked me about myself"
    song = "you were curious about the song"
    ask = "i asked you about the song"
    correct = "you guessed correctly"
    incorrect = "you guessed incorrectly"
    confuse = "you made me confused"

    def __init__(self):
        self.greeted = False
        self.purposed = False
        self.songs: set[str] = set()
        self.asked: set[str] = set()
        self.corrects = 0
        self.incorrects = 0
        self.confusions = 0

    def reflect(self) -> str:
        """Reflect on the interactions with the person"""

        interactions = []

        if self.greeted:
            interactions.append(self.greet)
        if self.purposed:
            interactions.append(self.purpose)
        if len(self.songs) > 0:
            songs = self.song
            if len(self.songs) == 1:
                songs += f" {list(self.songs)[0]}"
            else:
                songs += f"s {oxford(list(self.songs))}"
            interactions.append(songs)
        if len(self.asked) > 0:
            asked = self.ask
            if len(self.asked) == 1:
                asked += f" {list(self.asked)[0]}"
            else:
                asked += f"s {oxford(list(self.asked))}"
            interactions.append(asked)
        if self.confusions > 0:
            if self.confusions == 1:
                interactions.append(f"{self.confuse} at one point")
            else:
                interactions.append(f"{self.confuse} {self.confusions} times")
        if self.corrects > 0:
            if self.corrects == 1:
                interactions.append(f"{self.correct} once")
            else:
                interactions.append(f"{self.correct} {self.corrects} times")
        if self.incorrects > 0:
            if self.incorrects == 1:
                interactions.append(f"{self.incorrect} once")
            else:
                interactions.append(f"{self.incorrect} {self.incorrects} times")

        if len(interactions) == 0:
            return "sorry i don't know you... >.<"

        return f"i remember you! i remember that {oxford(interactions)}"

    def remember_greet(self):
        """Remember that the person was greeted"""
        self.greeted = True

    def remember_purpose(self):
        """Remember that the person asked about the bot's purpose"""
        self.purposed = True

    def remember_song(self, song: str):
        """Remember that the person asked about a song"""
        self.songs.add(song)

    def remember_ask(self, song: str):
        """Remember that the person was asked about a song"""
        self.asked.add(song)

    def remember_correct(self):
        """Remember that the person guessed correctly"""
        self.corrects += 1

    def remember_incorrect(self):
        """Remember that the person guessed incorrectly"""
        self.incorrects += 1

    def remember_confuse(self):
        """Remember that the person confused the bot"""
        self.confusions += 1


class TweetyBot:
    """Tweety Bot class for IRC"""

    def __init__(self, channel: str | None = None):
        self.irc = IRC(channel)
        self.ch = CommandHandler()
        self.mh = MusicHandler()

        self.interactions: dict[str, PersonMemory] = {}

        self.ch.add_command(
            Command(  # Hello
                phrases=["hello", "hi", "hey", "whats up"], callback=self.hello
            )
        )

        self.ch.add_command(
            Command(phrases=["forget"], callback=self.forget, exact=True)  # Forget
        )

        self.ch.add_command(  # Purpose
            Command(
                phrases=[
                    "purpose",
                    "What do you do?",
                    "What is your purpose?",
                    "Why are you here?",
                    "Who are you?",
                ],
                callback=self.purpose,
            )
        )

        self.ch.add_command(  # Remember
            Command(
                phrases=[
                    "remember me",
                    "Do you remember me?",
                    "Do you know me?",
                    "Do you know who I am?",
                    "Who am I?",
                ],
                callback=self.remember,
            )
        )

        self.ch.add_command(
            Command(  # Title of song
                phrases=[
                    "song name",
                    "What song was that?",
                    "What is that song called?",
                    "What is it called?",
                ],
                callback=self.song_title,
            )
        )

        self.ch.add_command(
            Command(  # Artist of song
                phrases=[
                    "song artist",
                    "who sang",
                    "Who sings that song?",
                    "Who made that song?",
                    "Who wrote that song?",
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
                    "When was that song written?",
                    "When did it come out?",
                    "When did that song come out?",
                ],
                callback=self.song_year,
            )
        )

        self.ch.add_command(
            Command(  # Genre of song
                phrases=[
                    "song genre",
                    "What genre is that song?",
                    "What kind of song is that?",
                ],
                callback=self.song_genre,
            )
        )

        for question_type in SongInfo:
            self.ch.add_command(
                Command(
                    phrases=[],
                    callback=self.rhetorical,
                    answer_type=question_type,
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
                assert message.sender is not None

                if message.is_for_bot():
                    command = self.ch.closest_command(threshold=0.2, min_diff=0.005)

                    if command is not None:
                        print(
                            f"\n[Matched phrase: {command.get_last_matched_phrase()}]\n"
                        )
                        response = command.run(command)
                        assert isinstance(response, Message)
                        self.irc.send(response)

                    else:
                        print("\n[No matching command for message]\n")
                        response = Message(
                            target=message.sender,
                            content="i don't understand what you're saying... >.<",
                        )
                        self.irc.send(response)
                else:
                    stanza = self.mh.next_stanza(message)
                    if stanza is not None:
                        print("\n[Matched a stanza]\n")
                        rhetorical_type = random.choice(list(SongInfo))

                        # likelihood to ask rhetorical
                        ask_rhetorical = random.random() <= 0.5

                        self.ch.new_stanza(
                            stanza, rhetorical_type if ask_rhetorical else None
                        )

                        self.irc.send(
                            Message(target=message.sender, content=f'"{stanza.stanza}"')
                        )

                        if ask_rhetorical:
                            self.person(message.sender).remember_ask(
                                f'"{stanza.title}"'
                            )
                            print(f"[Asking {message.sender} a rhetorical]\n")

                            response = self.add_rhetorical(
                                message.sender, rhetorical_type
                            )
                            self.irc.send(response)

        except KeyboardInterrupt:
            self.irc.send(Message(content="i have been terminated X.X"))
            self.irc.disconnect()

    def person(self, sender: str) -> PersonMemory:
        """Get the memory of a person"""
        if sender not in self.interactions:
            self.interactions[sender] = PersonMemory()
        return self.interactions[sender]

    def add_rhetorical(self, sender: str, rhetorical_type: SongInfo) -> Message:
        """Ask a rhetorical question"""
        stanza = self.mh.cur_stanza
        assert stanza is not None

        questions = {
            SongInfo.SONG_TITLE: "do you know the name of that song?",
            SongInfo.SONG_ARTIST: "do you know who wrote that?",
            SongInfo.SONG_YEAR: "do you know what year that song was released?",
            SongInfo.SONG_GENRE: "do you know the genre of that song?",
        }

        question = questions[rhetorical_type]
        self.ch.context.update_rhetorical(rhetorical_type, sender)
        return Message(target=sender, content=question)

    ### COMMANDS ###

    def rhetorical(self, command: Command) -> Message:
        """Rhetorical command"""
        answer_type = command.answer_type
        assert answer_type is not None
        context = self.ch.context
        latest_message = context.latest_message
        assert latest_message is not None and latest_message.sender is not None
        assert (
            self.mh.cur_stanza is not None
        ), "There should be a stanza... something is broken"
        assert latest_message.content is not None
        cur_stanza = self.mh.cur_stanza
        answers: dict[SongInfo, tuple[str, str]] = {
            SongInfo.SONG_TITLE: (cur_stanza.title, f"'s called {cur_stanza.title}"),
            SongInfo.SONG_ARTIST: (cur_stanza.artist, f"'s by {cur_stanza.artist}"),
            SongInfo.SONG_YEAR: (
                cur_stanza.year,
                f" was released in {cur_stanza.year}",
            ),
            SongInfo.SONG_GENRE: (cur_stanza.genre, f"'s {cur_stanza.genre}"),
        }
        actual, fill = answers[answer_type]
        s_actual = helpers.simplify(actual)
        s_latest_message = helpers.simplify(latest_message.content)
        guessed_correctly = s_actual in s_latest_message

        correct_bank = [
            f"yep! it{fill}",
            f"you got it! it{fill}",
            f"that's right! it{fill}",
        ]

        incorrect_bank = [
            f"nope, it{fill}",
            f"not quite, it{fill}",
            f"that's not it, it{fill}",
        ]

        bank = correct_bank if guessed_correctly else incorrect_bank
        choice = random.choice(bank)

        response = Message(target=latest_message.sender, content=choice)

        if command.already_ran:
            response.content = (
                "i already answered that haha but that's okay... " + choice
            )
        elif context.cur_rhet is answer_type:
            if latest_message.sender == context.cur_rhet_target:
                feedback = (
                    "ding-ding-ding!" if guessed_correctly else "wah wah waaah..."
                )
                response.content = f"{feedback} {choice}"
                if guessed_correctly:
                    self.person(latest_message.sender).remember_correct()
                else:
                    self.person(latest_message.sender).remember_incorrect()
            else:
                response.content = (
                    f"i didn't ask you... but {choice} (sorry "
                    + f"${context.cur_rhet_target}, the beans have been spilled)"
                )
            command.already_ran = True
        else:
            command.already_ran = True

        return response

    def hello(self, _: Command) -> Message:
        """Hello command"""
        latest_message = self.ch.context.latest_message
        assert latest_message is not None and latest_message.sender is not None

        self.person(latest_message.sender).remember_greet()

        return Message(
            target=latest_message.sender,
            content=random.choice(
                ["hey :)", "heya!", "hey :3c", "^.^", "umm hi... >.<"]
            ),
        )

    def forget(self, _: Command) -> Message:
        """Forget command"""
        latest_message = self.ch.context.latest_message
        assert latest_message is not None

        self.ch.reset()
        self.mh.forget()
        self.interactions = {}

        print("[Forgot everything]\n")

        return Message(
            target=latest_message.sender,
            content="oh okay i'll do tha... wait who are you?",
        )

    def purpose(self, _: Command) -> Message:
        """Purpose command"""
        latest_message = self.ch.context.latest_message
        assert latest_message is not None and latest_message.sender is not None

        purpose = (
            "my name is tweety and i have a habit of eavesdropping on "
            + "conversations and singing songs that sound similar... i might even ask "
            + "you a question about it. but if you want to know anything, you can ask "
            + 'me question about the song i sang like "what is that song called?" '
            + '"who wrote that song?", "what genre is that song?", and "when was that '
            + "song released?\". i'll understand you if you're direct otherwise i "
            + "might not understand... *-*"
        )

        self.person(latest_message.sender).remember_purpose()

        return Message(
            target=latest_message.sender,
            content=purpose,
        )

    def remember(self, _: Command) -> Message:
        """Remember command"""
        latest_message = self.ch.context.latest_message
        assert latest_message is not None
        sender = latest_message.sender
        assert sender is not None

        if sender not in self.interactions:
            self.interactions[sender] = PersonMemory()

        memory = self.interactions[sender]

        return Message(target=sender, content=memory.reflect())

    def song_title(self, command: Command) -> Message:
        """Song name command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None and latest_message.sender is not None

        if cur_stanza is None:
            self.person(latest_message.sender).remember_confuse()
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        bank = [
            f'it\'s called "{cur_stanza.title}"',
            f'it\'s "{cur_stanza.title}" by {cur_stanza.artist}',
            f"i'm surprised you don't know! it's \"{cur_stanza.title}\" by {cur_stanza.artist}",
        ]

        choice = random.choice(bank)

        response = Message(target=latest_message.sender, content=choice)

        if context.cur_rhet is SongInfo.SONG_TITLE:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3c"
                )
        elif command.already_ran:
            response.content = "i already said that haha but that's okay... " + choice
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')
        else:
            command.already_ran = True
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')

        return response

    def song_artist(self, command: Command) -> Message:
        """Song artist command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None and latest_message.sender is not None

        if cur_stanza is None:
            self.person(latest_message.sender).remember_confuse()
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        bank = [
            f"it's by {cur_stanza.artist}",
            f"it's by {cur_stanza.artist}, of course!",
            f"you don't know? it's by {cur_stanza.artist}!",
        ]

        choice = random.choice(bank)

        response = Message(target=latest_message.sender, content=choice)

        if context.cur_rhet is SongInfo.SONG_ARTIST:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3c"
                )
        elif command.already_ran:
            response.content = "i already said that haha but that's okay... " + choice
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')
        else:
            command.already_ran = True
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')

        return response

    def song_year(self, command: Command) -> Message:
        """Song year command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None and latest_message.sender is not None

        if cur_stanza is None:
            self.person(latest_message.sender).remember_confuse()
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        bank = [
            f"it was released in {cur_stanza.year}",
            f"i think i remember first hearing it in {cur_stanza.year}",
            f"you don't remember? it was released in {cur_stanza.year}!",
        ]

        choice = random.choice(bank)

        response = Message(target=latest_message.sender, content=choice)

        if context.cur_rhet is SongInfo.SONG_YEAR:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3c"
                )
        elif command.already_ran:
            response.content = "i already said that haha but that's okay... " + choice
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')
        else:
            command.already_ran = True
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')

        return response

    def song_genre(self, command: Command) -> Message:
        """Song genre command"""
        context = self.ch.context
        latest_message = context.latest_message
        cur_stanza = self.mh.cur_stanza

        assert latest_message is not None and latest_message.sender is not None

        if cur_stanza is None:
            self.person(latest_message.sender).remember_confuse()
            return Message(
                target=latest_message.sender,
                content="i'm not sure what you're referring to...",
            )

        bank = [
            f"it's kind of a {cur_stanza.genre} song",
            f"i'd say it's probably a {cur_stanza.genre} song",
            f"it's {cur_stanza.genre}, of course!",
        ]

        choice = random.choice(bank)

        response = Message(target=latest_message.sender, content=choice)

        if context.cur_rhet is SongInfo.SONG_GENRE:
            if latest_message.sender == context.cur_rhet_target:
                response.content = "take a guess, that's what i asked you hehe >.<"
            else:
                response.content = (
                    f"that's what i asked {latest_message.sender}, "
                    + "i wanna see if they know :3c"
                )
        elif command.already_ran:
            response.content = "i already said that haha but that's okay... " + choice
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')
        else:
            command.already_ran = True
            self.person(latest_message.sender).remember_song(f'"{cur_stanza.title}"')

        return response

    def die(self, _: Command) -> Message:
        """Die command"""
        latest_message = self.ch.context.latest_message
        assert latest_message is not None

        return Message(
            target=latest_message.sender,
            content="aww okay, goodbye... X.X",
            cb=self.irc.disconnect(),
        )
