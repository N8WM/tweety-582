"""Command handler for the bot"""

from typing import Callable

import torch

from .embeddings import embed, most_similar


class Command:
    """Class for a singular command"""

    def __init__(self, phrases: list[str], callback: Callable):
        self.phrases = phrases
        self.callback = callback
        self.phrase_embedings = torch.stack([embed(phrase) for phrase in phrases])
        self.lmp_idx: int | None = None

    def run(self, *args, **kwargs):
        """Run the command"""
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

    def closest_command(
        self, phrase: str, threshold: float = 0, min_diff: float = 0
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
        sim_scores: list[float] = []
        phrase_idxs: list[int] = []

        if len(self.commands) == 0:
            return None

        for command in self.commands:
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
            command = self.commands[max_command_idx]
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

        command = self.commands[max_command_idx]
        command.lmp_idx = phrase_idxs[max_command_idx]
        return command

    def add_command(self, phrases: list[str], callback: Callable) -> Command:
        """Add a command to the handler"""
        command = Command(phrases, callback)
        self.commands.append(command)
        return command


if __name__ == "__main__":
    # Test the CommandHandler
    ch = CommandHandler()

    ch.add_command(["hello", "hi", "hey"], lambda: print("Hello!"))
    ch.add_command(["die", "kill", "end", "terminate"], lambda: print("Die!"))
    ch.add_command(
        ["song name", "What song was that?", "What is that song called?"],
        lambda: print("The song name is 'Never Gonna Give You Up'."),
    )
    ch.add_command(
        ["song artist", "who", "who sang", "Who sings that song?"],
        lambda: print("The artist is Rick Astley."),
    )
    ch.add_command(
        ["song year", "when", "song release date", "When was that song made?"],
        lambda: print("The song was released in 1987."),
    )
    ch.add_command(
        ["song genre", "What genre is that song?"], lambda: print("The song is pop.")
    )

    while True:
        phr = input("Enter a phrase: ")
        cmd = ch.closest_command(phr, 0.2, 0.1)
        if cmd:
            print("Last matched phrase:", cmd.get_last_matched_phrase())
            cmd.run()
        else:
            print("No command found.")
