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

Running `python src/main.py` with the example profile (`genre=pop`, `mood=happy`, `energy=0.8`) produces:

```text
Loaded songs: 20

Top recommendations:

Sunrise City - Score: 9.94
Because: Exact genre match: pop (+4); Exact mood match: happy (+3); Energy: 0.82 vs preferred 0.80, difference 0.02 (+2.94)

Rooftop Lights - Score: 7.88
Because: Related genres: indie pop and pop (+2); Exact mood match: happy (+3); Energy: 0.76 vs preferred 0.80, difference 0.04 (+2.88)

Gym Hero - Score: 6.61
Because: Exact genre match: pop (+4); No mood match: intense vs happy (+0); Energy: 0.93 vs preferred 0.80, difference 0.13 (+2.61)

Brass Boulevard - Score: 5.85
Because: No genre match: salsa vs pop (+0); Exact mood match: happy (+3); Energy: 0.85 vs preferred 0.80, difference 0.05 (+2.85)

Afterhours Steps - Score: 5.76
Because: No genre match: house vs pop (+0); Exact mood match: happy (+3); Energy: 0.88 vs preferred 0.80, difference 0.08 (+2.76)
```

---

## Experiments You Tried

Tested **Mus10 v1.0** on 18 profiles against the 20-song catalog, requesting five recommendations per profile. The temporary **weight shift** halved genre points (exact: 4 to 2; related: 2 to 1) and doubled energy points (maximum: 3 to 6). Mood points stayed unchanged.

Profiles below use **genre / mood / energy**. Original scores are **out of 10**; shifted scores are **out of 11**, so larger raw scores do not mean better recommendations.

| Experiment / profile | Original result | Weight-shift result | What we learned |
|---|---|---|---|
| Baseline: pop / happy / 0.8 | Top three: Sunrise City (9.94), Rooftop Lights (7.88), Gym Hero (6.61) | Top three: Sunrise City (10.88), Rooftop Lights (9.76), Brass Boulevard (8.70) | Same top-five songs, but Gym Hero drops from 3rd to 5th. |
| Minimum energy: classical / relaxed / 0 | Quiet Constellations first (9.64) | Quiet Constellations first (10.28) | All five ranks stay unchanged; the lower boundary is accepted. |
| Maximum energy: metal / intense / 1 | Ember Breaker first (9.94) | Ember Breaker first (10.88) | All five ranks stay unchanged; the upper boundary is accepted. |
| Conflicting tastes: metal / relaxed / 0 | Quiet Constellations first (5.64); Ember Breaker 4th | Quiet Constellations first (8.28); Ember Breaker leaves the top five and Library Rain enters | More emphasis on energy closeness can displace the preferred genre. |
| High-energy ambient: ambient / chill / 1 | Spacewalk Thoughts first (7.84); Midnight Coding and Library Rain in the top five | Spacewalk Thoughts first (6.68); Ember Breaker and Gym Hero replace those two songs | The winner still has energy 0.28, but the rest of the list shifts toward higher energy. |
| Unknown genre: opera / happy / 0.8 | Sunrise City first (5.94) | Sunrise City first (8.88) | All five ranks stay unchanged; mood and energy determine the results. |
| Unknown mood: pop / nostalgic / 0.8 | Sunrise City first (6.94); Paper Kite Goodbye 4th | Sunrise City first (7.88); Paper Kite Goodbye leaves and Night Drive Loop enters | Lower-ranked songs change even when the top three stay the same. |
| Both unknown: opera / nostalgic / 0.5 | Island Afternoon first (2.91) | Island Afternoon first (5.82) | Energy alone determines the ranking; all five ranks stay unchanged. |
| Blank genre and mood, energy 0.5 | Island Afternoon first (2.91) | Island Afternoon first (5.82) | Blank labels are accepted and produce the same ranking as unknown labels. |
| Case and spaces: `"  POP  "` / `" HAPPY "` / 0.8 | Same as original baseline | Same as shifted baseline | Normalization works under both weighting schemes. |
| Acoustic preference on and off (2 profiles): baseline plus `likes_acoustic=True/False` | Both match original baseline | Both match shifted baseline | Acoustic preference has no effect. |
| Invalid energy (4 profiles): baseline with -0.1, 1.1, NaN, or positive infinity | `ValueError` for all four | Same errors | Both schemes reject out-of-range and nonfinite energy. |
| Missing energy: pop / happy / omitted | `KeyError: 'energy'` | Same error | There is no default energy or friendly missing-field message. |
| Text energy: pop / happy / `"0.8"` | `TypeError` | Same error | Numeric strings are not converted automatically. |

Across the **12 valid profiles**, no first-place recommendation changed, **7 top-five orderings changed**, and **3 top-five memberships changed**. These counts include the formatting and two acoustic checks that repeat the baseline's behavior; excluding those three, 4 of 9 orderings and 3 of 9 memberships changed. The six invalid profiles produced the same exceptions under both schemes. All 480 valid profile-song scores across the two schemes were checked against independently calculated formulas.

The experiment shows sensitivity in the full recommendation list even when the winner stays fixed. Increasing energy's importance can reduce genre fidelity, but it does not fix missing catalog coverage or ignored acoustic preferences. No listener study established which weights are better. The experiment ran in memory; `src/main.py` and `src/recommender.py` remain unchanged, with the original weights active. See the [Mus10 v1.0 model card](model_card.md#7-evaluation) for detailed scores and bias analysis.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)



