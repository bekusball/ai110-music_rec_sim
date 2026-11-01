import csv
from math import isfinite

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load song dictionaries with integer IDs and float musical attributes.
    """
    songs = []
    numeric_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            # CSV values are strings; convert numeric fields for scoring and ranking.
            row["id"] = int(row["id"])
            for field in numeric_fields:
                row[field] = float(row[field])
            songs.append(row)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Return a score out of 10 and reasons for the genre, mood, and energy points.
    """
    preferred_energy = user_prefs["energy"]
    song_energy = song["energy"]
    for label, energy in (("Preferred", preferred_energy), ("Song", song_energy)):
        if not isfinite(energy) or not 0 <= energy <= 1:
            raise ValueError(f"{label} energy must be finite and between 0 and 1")

    # Normalize comparisons without changing the original profile or song.
    preferred_genre = user_prefs["genre"].strip().lower()
    song_genre = song["genre"].strip().lower()
    preferred_mood = user_prefs["mood"].strip().lower()
    song_mood = song["mood"].strip().lower()
    reasons = []

    # Exact and related matches are alternatives, so their points never stack.
    if song_genre == preferred_genre:
        genre_points = 4
        reasons.append(f"Exact genre match: {song_genre} (+4)")
    elif {song_genre, preferred_genre} == {"pop", "indie pop"}:
        genre_points = 2
        reasons.append(f"Related genres: {song_genre} and {preferred_genre} (+2)")
    else:
        genre_points = 0
        reasons.append(f"No genre match: {song_genre} vs {preferred_genre} (+0)")

    related_moods = {"chill", "relaxed", "focused"}
    if song_mood == preferred_mood:
        mood_points = 3
        reasons.append(f"Exact mood match: {song_mood} (+3)")
    elif song_mood in related_moods and preferred_mood in related_moods:
        mood_points = 1.5
        reasons.append(f"Related moods: {song_mood} and {preferred_mood} (+1.5)")
    else:
        mood_points = 0
        reasons.append(f"No mood match: {song_mood} vs {preferred_mood} (+0)")

    energy_difference = abs(song_energy - preferred_energy)
    energy_points = 3 * (1 - energy_difference)
    reasons.append(
        f"Energy: {song_energy:.2f} vs preferred {preferred_energy:.2f}, "
        f"difference {energy_difference:.2f} (+{energy_points:.2f})"
    )
    return genre_points + mood_points + energy_points, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Return the top k (song, score, explanation) tuples from the full catalog.
    """
    if not songs or k <= 0:
        return []

    recommendations = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        recommendations.append((song, score, "; ".join(reasons)))

    # Keep full score precision; break ties by energy distance, then numeric ID.
    recommendations.sort(key=lambda rec: (
        -rec[1],
        abs(rec[0]["energy"] - user_prefs["energy"]),
        int(rec[0]["id"]),
    ))
    return recommendations[:k]
