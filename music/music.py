"""Music module for the bot"""

from enum import Enum

from irc.message import Message


class SongInfo(Enum):
    """Rhetorical question enum"""

    SONG_TITLE = "song name"
    SONG_ARTIST = "song artist"
    SONG_YEAR = "song year"
    SONG_GENRE = "song genre"


class Stanza:
    """Class for a song with a stanza"""

    def __init__(self, title: str, artist: str, year: str, genre: str, stanza: str):
        self.title = title
        self.artist = artist
        self.year = year
        self.genre = genre
        self.stanza = stanza


class MusicHandler:
    """Class for handling music"""

    def __init__(self):
        self.cur_stanza: Stanza | None = None

    def next_stanza(self, message: Message) -> Stanza:
        """Get the next stanza if available"""
        return Stanza("", "", "", "", "")
