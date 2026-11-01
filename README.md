# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

- **Scoring:** Match each song's genre, mood, and energy to the user's preferences.
- **User profile:** Stores favorite genre, favorite mood, target energy, and an acoustic preference (unused in this scoring rule).
- **Genre score:** 4 points for an exact match, 2 for related genres (pop and indie pop), otherwise 0.
- **Mood score:** 3 points for an exact match, 1.5 for related moods (chill, relaxed, and focused), otherwise 0.
- **Energy score:** `3 * (1 - abs(song_energy - target_energy))`; both energy values range from 0 to 1, so closer matches earn more points.
- **Recommendations:** Add the points for a score out of 10 and return the top `k` songs, highest score first. Break ties by closer energy, then lower song ID, and explain each recommendation.

---

## Getting Started

### Setup

Run these commands from the project folder.

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   ```

   Activate it using the command for your shell:

   - Mac or Linux: `source .venv/bin/activate`
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`

2. Install dependencies

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python src/main.py
   ```

   The app loads the CSV and prints `Loaded songs: 20`, followed by the top five
   recommendations with scores and explanations. For the example profile, the
   top three are Sunrise City (9.94), Rooftop Lights (7.88), and Gym Hero (6.61).
   The functional API is implemented; the `Recommender` class remains a starter stub.

### Running Tests

Run the starter tests with:

```bash
python -m pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



