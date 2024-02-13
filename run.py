"""Script to run our bot"""

import argparse

from bot.tweety import TweetyBot
from music.setup import setup

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the bot")
    parser.add_argument(
        "-c", type=str, help="Channel: the channel to join", required=False
    )
    args = parser.parse_args()
    channel = args.c

    setup()

    tweety = TweetyBot(channel=channel)
    tweety.start()
