"""Command handler for the bot"""

from typing import Callable

import torch

from irc import Message
from music.music import SongInfo, Stanza

from . import helpers
from .embeddings import embed, most_similar


class Context:
    """Class for a command context"""

    def __init__(self):
        self.latest_message: Message | None = None
        self.cur_stanza: Stanza | None = None
        self.cur_rhet: SongInfo | None = None
        self.cur_rhet_target: str | None = None

    def update_latest_message(self, msg: Message) -> None:
        """Set the latest message"""
        self.latest_message = msg

    def update_rhetorical(self, rhet: SongInfo, target: str | None) -> None:
        """Set the current rhetorical question"""
        self.cur_rhet = rhet
        self.cur_rhet_target = target

    def clear(self) -> None:
        """Clear the context (sans message)"""
        self.cur_stanza = None
        self.cur_rhet = None
        self.cur_rhet_target = None

    def has_rhetorical(self) -> bool:
        """Check if a rhetorical question is active"""
        return self.cur_rhet is not None


class Command:
    """Class for a singular command"""

    def __init__(
        self, phrases: list[str], callback: Callable, run_once=False, exact=False
    ):
        self.phrases = phrases
        self.callback = callback
        self.run_once = run_once
        self.exact = exact
        self.context: Context | None = None
        self.phrase_embedings = torch.stack([embed(phrase) for phrase in phrases])
        self.lmp_idx: int | None = None
        self.already_ran = False

    def run(self, remove: Callable, *args, **kwargs):
        """Run the command, remove if `run_once` is `True`"""
        if self.run_once:
            remove(self)
        return self.callback(*args, **kwargs)

    def get_last_matched_phrase(self) -> str | None:
        """Get the last matched phrase"""
        if self.lmp_idx is not None:
            return self.phrases[self.lmp_idx]
        return None


class CommandHandler:
    """Class for handling commands"""

    def __init__(self):
        self.commands: list[Command] = []
        self.context = Context()

    def reset(self) -> None:
        """Reset the command handler"""
        self.commands = [c for c in self.commands if not c.run_once]
        for command in self.commands:
            command.lmp_idx = None
            command.already_ran = False
        # Say something like "never mind"?
        self.context.clear()

    def new_message(self, message: Message) -> None:
        """Update the context with a new message"""
        self.context.update_latest_message(message)

    def new_stanza(self, stanza: Stanza, rhetorical: SongInfo | None = None) -> None:
        """Reset and update the context with a new stanza"""
        assert self.context.latest_message is not None

        self.reset()
        self.context.cur_stanza = stanza

        if rhetorical:
            self.context.update_rhetorical(
                rhetorical, self.context.latest_message.sender
            )

    def closest_command(
        self, threshold: float = 0, min_diff: float = 0
    ) -> Command | None:
        """
        Return the closest command to the input phrase, with an optional minimum
        similarity score.
        Args:
        - `phrase` (`str`): The phrase to compare.
        - `threshold` (`float`): The minimum similarity score to consider.
        - `min_diff` (`float`): The minimum difference from the next most
          similar command to consider.
        Returns:
        - `Command | None`: The closest command to the phrase, or `None` if no
          command is close enough.
        """
        assert self.context.latest_message is not None
        phrase = self.context.latest_message.content
        assert isinstance(phrase, str)

        sim_scores: list[float] = []
        phrase_idxs: list[int] = []

        exact_commands = [c for c in self.commands if c.exact]
        soft_commands = [c for c in self.commands if not c.exact]

        # check for exact matches

        for command in exact_commands:
            if helpers.simplify(phrase) in command.phrases:
                idx = command.phrases.index(helpers.simplify(phrase))
                command.lmp_idx = idx
                return command

        # no exact matches, check for soft matches

        if len(soft_commands) == 0:
            return None

        for command in soft_commands:
            if helpers.simplify(phrase) in command.phrases:
                idx = command.phrases.index(helpers.simplify(phrase))
                command.lmp_idx = idx
                return command
            idx, score = most_similar(phrase, command.phrase_embedings)
            sim_scores.append(score)
            phrase_idxs.append(idx)

        max_score = max(sim_scores)
        max_command_idx = sim_scores.index(max_score)
        meets_thresh_req = sim_scores[max_command_idx] >= threshold

        if not meets_thresh_req:
            print(f"!threshold ({sim_scores[max_command_idx]} < {threshold})")
            return None

        if len(sim_scores) == 1:
            command = soft_commands[max_command_idx]
            command.lmp_idx = phrase_idxs[max_command_idx]
            return command

        # get index of second highest score
        next_max_score = max(
            sim_scores[:max_command_idx] + sim_scores[max_command_idx + 1 :]
        )
        meets_diff_req = max_score - next_max_score >= min_diff

        if not meets_diff_req:
            print(f"!min_diff ({max_score - next_max_score} < {min_diff})")
            return None

        command = soft_commands[max_command_idx]
        command.lmp_idx = phrase_idxs[max_command_idx]
        return command

    def add_command(self, command: Command) -> None:
        """Add a command to the handler"""
        command.context = self.context
        self.commands.append(command)

    def add_rhetorical_command(
        self,
        command: Command,
        question_type: SongInfo,
        question_target: str | None = None,
    ) -> None:
        """Add a rhetorical command to the handler"""
        command.context = self.context
        self.commands.append(command)
        self.context.update_rhetorical(question_type, question_target)


if __name__ == "__main__":
    # Test the CommandHandler
    ch = CommandHandler()

    ch.add_command(Command(["hello", "hi", "hey"], lambda: print("Hello!")))
    ch.add_command(Command(["die", "kill", "end", "terminate"], lambda: print("Die!")))
    ch.add_command(
        Command(
            ["song name", "What song was that?", "What is that song called?"],
            lambda: print("The song name is 'Never Gonna Give You Up'."),
        )
    )
    ch.add_command(
        Command(
            ["song artist", "who", "who sang", "Who sings that song?"],
            lambda: print("The artist is Rick Astley."),
        )
    )
    ch.add_command(
        Command(
            ["song year", "when", "song release date", "When was that song made?"],
            lambda: print("The song was released in 1987."),
        )
    )
    ch.add_command(
        Command(
            ["song genre", "What genre is that song?"],
            lambda: print("The song is pop."),
        )
    )

    while True:
        phr = input("Enter a phrase: ")
        mes = Message(content=phr)
        ch.new_message(mes)
        cmd = ch.closest_command(0.2, 0.1)
        if cmd:
            print("Last matched phrase:", cmd.get_last_matched_phrase())
            cmd.run(lambda: ch.commands.remove)
        else:
            print("No command found.")
