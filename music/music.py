"""Music module for the bot"""
import re
import json
import random
import pandas as pd
import torch.nn.functional as F
from collections import Counter
from nltk.stem import PorterStemmer

from enum import Enum

from irc.message import Message
from bot.commands import embeddings as em

porter_stemmer = PorterStemmer()

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
        self.inverse_index: dict | None = None
        self.exploded_song_df: pd.DataFrame | None = None

        self.inverse_index, self.exploded_song_df = self.read_files()

    def next_stanza(self, message: Message) -> Stanza:
        """Get the next stanza if available"""
        phrase = message.content
        assert phrase is not None

        verse = self.get_verse(phrase, self.inverse_index, self.exploded_song_df)
        shortened_verse = self.shorten_verse(phrase, verse['verse'])

        assert shortened_verse is not None
        assert self.inverse_index is not None
        assert self.exploded_song_df is not None

        shortened_verse = ("/ " + shortened_verse + "...").strip()

        percentile = self.get_song_percentile(verse['views'], self.exploded_song_df['views'])

        assert isinstance(shortened_verse, str)

        similarity_score = self.get_similarity_score(phrase, shortened_verse)
        if similarity_score > 0.2 and random.randint(0, 100) < percentile:
            self.cur_stanza = Stanza(verse["title"], verse["artist"], verse["year"], verse["genre"], shortened_verse)
        else:
            self.cur_stanza = None

        return self.cur_stanza


    def read_files(self):
        with open('music/inverse_index.json') as f:
            inverse_index = json.load(f)
        exploded_song_df = pd.read_csv('music/exploded_song_df.csv')
        return inverse_index, exploded_song_df


    def get_common_verses(self, words, inverse_index):
        songs = []
        for word in words:
            if word in inverse_index:
                songs.extend(inverse_index[word])

        return songs


    def get_familiar_songs(self, phrase, inverse_index):
        words = phrase.lower().split()
        song_ids = self.get_common_verses(words, inverse_index)

        counter = Counter(song_ids)
        max_count = counter.most_common(1)[0][1]
        song_ids = [item for item, count in counter.items() if count == max_count]

        return song_ids


    def get_most_popular_song(self, song_ids, exploded_song_df):
        df = exploded_song_df.iloc[song_ids]  
        return df.sort_values('views', ascending=False).iloc[0]


    def get_verse(self, phrase, inverse_index, exploded_song_df):
        phrase = porter_stemmer.stem(phrase)
        song_ids = self.get_familiar_songs(phrase, inverse_index)
        verse = self.get_most_popular_song(song_ids, exploded_song_df)
        return verse


    def get_song_percentile(self, song_views, views_col):
        p = views_col.values.searchsorted(song_views) / len(views_col) * 100
        return p


    def shorten_verse(self, phrase, verse):
        words = phrase.lower().split()
        lines = re.split('[,()]', verse)

        max_word_count = 0
        line_with_most_words = None

        for line in lines:
            word_count = sum(1 for word in words if word.lower() in line.lower())
            if word_count > max_word_count:
                max_word_count = word_count
                line_with_most_words = line

        return line_with_most_words


    def get_similarity_score(self, phrase, verse):
        p_em = em.embed(phrase)
        v_em = em.embed(verse)
        return F.cosine_similarity(p_em, v_em, dim=0)


if __name__ == "__main__":
    phrase = "I used to rule the world"
    message = Message(raw_message=None, content=phrase)  # type: ignore

    music_handler = MusicHandler()
    stanza = music_handler.next_stanza(message)

    print(phrase)
    print(stanza.stanza)
    print(stanza.title, stanza.artist, stanza.year, stanza.genre)
