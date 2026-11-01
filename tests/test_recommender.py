from pathlib import Path

import pytest

from src.recommender import (
    Song, UserProfile, Recommender, load_songs, score_song, recommend_songs,
)


@pytest.mark.parametrize("preferred, actual, points", [
    ("pop", "pop", 4),
    (" POP ", " Pop ", 4),
    ("pop", "indie pop", 2),
    ("indie pop", "pop", 2),
    ("pop", "rock", 0),
])
def test_score_song_genre_points(preferred, actual, points):
    prefs = {"genre": preferred, "mood": "happy", "energy": 0.5}
    song = {"genre": actual, "mood": "intense", "energy": 0.5}

    score, _ = score_song(prefs, song)

    assert score == pytest.approx(points + 3)


@pytest.mark.parametrize("preferred, actual, points", [
    ("happy", "happy", 3),
    (" CHILL ", " Chill ", 3),
    ("chill", "relaxed", 1.5),
    ("relaxed", "chill", 1.5),
    ("chill", "focused", 1.5),
    ("focused", "chill", 1.5),
    ("relaxed", "focused", 1.5),
    ("focused", "relaxed", 1.5),
    ("happy", "intense", 0),
])
def test_score_song_mood_points(preferred, actual, points):
    prefs = {"genre": "pop", "mood": preferred, "energy": 0.5}
    song = {"genre": "rock", "mood": actual, "energy": 0.5}

    score, _ = score_song(prefs, song)

    assert score == pytest.approx(points + 3)


@pytest.mark.parametrize("preferred, actual, expected", [
    (0, 0, 3), (1, 1, 3), (0, 1, 0), (1, 0, 0),
    (0.8, 0.3, 1.5), (0.3, 0.8, 1.5),
])
def test_score_song_energy_points(preferred, actual, expected):
    prefs = {"genre": "pop", "mood": "happy", "energy": preferred}
    song = {"genre": "rock", "mood": "intense", "energy": actual}

    score, _ = score_song(prefs, song)

    assert score == pytest.approx(expected)


@pytest.mark.parametrize("target", ["user", "song"])
@pytest.mark.parametrize("energy", [-0.01, 1.01, float("nan"), float("inf"), -float("inf")])
def test_score_song_rejects_invalid_energy(target, energy):
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = dict(prefs)
    (prefs if target == "user" else song)["energy"] = energy

    with pytest.raises(ValueError, match="energy"):
        score_song(prefs, song)


def test_score_song_explains_matches_and_energy_without_using_other_features():
    prefs = {"genre": "pop", "mood": "chill", "energy": 0.8}
    song = {"genre": "indie pop", "mood": "relaxed", "energy": 0.6}

    score, reasons = score_song(prefs, song)

    assert score == pytest.approx(5.9)
    assert isinstance(reasons, list)
    explanation = " ".join(reasons).lower()
    for detail in ("genre", "pop", "indie pop", "mood", "chill", "relaxed", "energy", "0.60", "0.80", "0.20"):
        assert detail in explanation
    assert score_song({**prefs, "likes_acoustic": True}, {
        **song, "id": 999, "acousticness": 1, "tempo_bpm": 200,
        "valence": 0, "danceability": 0,
    }) == (score, reasons)


def test_recommend_songs_scores_entire_catalog_and_preserves_input():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    songs = load_songs(str(Path(__file__).resolve().parents[1] / "data" / "songs.csv"))
    original = [dict(song) for song in songs]

    results = recommend_songs(prefs, songs, k=3)

    assert [song["title"] for song, _, _ in results] == [
        "Sunrise City", "Rooftop Lights", "Gym Hero",
    ]
    assert [score for _, score, _ in results] == pytest.approx([9.94, 7.88, 6.61])
    for song, score, explanation in results:
        expected_score, reasons = score_song(prefs, song)
        assert score == expected_score
        assert isinstance(explanation, str)
        assert all(reason in explanation for reason in reasons)
        assert any(song is original_song for original_song in songs)
    assert songs == original


def test_recommend_songs_breaks_score_ties_by_energy_then_numeric_id():
    prefs = {"genre": "pop", "mood": "chill", "energy": 1.0}
    songs = [
        {"id": "1", "genre": "pop", "mood": "chill", "energy": 0.5},
        {"id": "10", "genre": "pop", "mood": "relaxed", "energy": 1.0},
        {"id": "2", "genre": "pop", "mood": "focused", "energy": 1.0},
    ]

    results = recommend_songs(prefs, songs)

    assert [song["id"] for song, _, _ in results] == ["2", "10", "1"]
    assert [score for _, score, _ in results] == [8.5, 8.5, 8.5]


def test_recommend_songs_does_not_round_scores_before_ranking():
    prefs = {"genre": "pop", "mood": "chill", "energy": 1.0}
    songs = [
        {"id": 1, "genre": "pop", "mood": "relaxed", "energy": 1.0},
        {"id": 2, "genre": "pop", "mood": "chill", "energy": 0.5001},
    ]

    results = recommend_songs(prefs, songs)

    assert [song["id"] for song, _, _ in results] == [2, 1]
    assert results[0][1] == pytest.approx(8.5003)


@pytest.mark.parametrize("k, expected_count", [(-1, 0), (0, 0), (1, 1), (5, 2)])
def test_recommend_songs_respects_k(k, expected_count):
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    songs = [{"id": song_id, **prefs} for song_id in (1, 2)]

    assert len(recommend_songs(prefs, songs, k)) == expected_count


def test_recommend_songs_returns_empty_list_for_empty_catalog():
    assert recommend_songs({}, []) == []


def test_load_songs_preserves_text_and_converts_numeric_fields(tmp_path):
    csv_path = tmp_path / "songs.csv"
    csv_path.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
        '7,"Rain, Again",Beyoncé,pop,happy,0.82,118,0.84,0.79,0.18\n',
        encoding="utf-8",
    )

    songs = load_songs(str(csv_path))

    assert songs == [{
        "id": 7,
        "title": "Rain, Again",
        "artist": "Beyoncé",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.82,
        "tempo_bpm": 118.0,
        "valence": 0.84,
        "danceability": 0.79,
        "acousticness": 0.18,
    }]
    assert isinstance(songs[0]["id"], int)
    for field in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
        assert isinstance(songs[0][field], float)


def test_load_songs_returns_empty_list_for_header_only_csv(tmp_path):
    csv_path = tmp_path / "songs.csv"
    csv_path.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n",
        encoding="utf-8",
    )

    assert load_songs(str(csv_path)) == []

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
