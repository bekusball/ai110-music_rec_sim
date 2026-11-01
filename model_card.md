# Model Card: Mus10 v1.0

## 1. Model Name

**Mus10 v1.0**

A rule-based music recommender. This card describes the functional recommender used by `src/main.py`. The weight shift below was a temporary sensitivity experiment, not a permanent change to v1.0.

## 2. Intended Use

Mus10 recommends five songs from a small catalog for classroom exploration. A user supplies one preferred genre, one mood, and a target energy between 0 and 1. The system assumes these three preferences describe what the user wants to hear right now.

It demonstrates how scoring choices affect recommendations. It has not been evaluated with real listeners and is not a personalized music service trained on listening history.

## 3. How the Model Works

Every song earns points for genre, mood, and closeness to the user's energy target. The system adds the points, ranks the entire catalog, and returns the highest-scoring songs with explanations. It ignores capitalization and surrounding spaces in genre and mood labels.

| Component | Original model | Temporary weight shift |
|---|---|---|
| Exact genre match | 4 points | 2 points |
| Related genre match: pop and indie pop | 2 points | 1 point |
| Exact mood match | 3 points | 3 points |
| Related moods: chill, relaxed, focused | 1.5 points | 1.5 points |
| Energy closeness | Up to 3 points | Up to 6 points |
| Maximum total | 10 points | 11 points |

An exact energy match receives all energy points. Points decrease linearly with the absolute energy difference; opposite endpoints receive zero. Exact and related category bonuses do not stack. Unmatched categories receive zero points. Ties are resolved by closer energy, then lower numeric song ID, using unrounded scores.

The functional implementation loads numeric song attributes, scores the full catalog, validates energy, and explains its decisions. The separate `Recommender` class still contains starter placeholders; these findings apply to the functional API used by the command-line app.

## 4. Data

The unchanged `data/songs.csv` contains **20 songs across 16 genres and 6 moods**. There is no training step or train/test split; the CSV is the recommendation catalog.

- Genre counts: lofi has 3 songs; pop and indie pop have 2 each; rock, ambient, jazz, synthwave, folk, house, hip hop, classical, metal, reggae, country, salsa, and r&b have 1 each.
- Mood counts: happy, chill, and moody have 4 songs each; intense and relaxed have 3 each; focused has 2.
- The catalog also includes artist, tempo, valence, danceability, and acousticness. These do not affect scoring. Song ID is used only for tie-breaking.

The catalog cannot represent the full range of musical taste. For example, opera is absent, and the data provides no lyrics, language, listening history, or user feedback. No songs were added or removed for this experiment.

## 5. Strengths

The system makes its decisions easy to inspect: each recommendation explains its genre, mood, and energy contributions. Results are deterministic for a fixed catalog and profile.

Both tested weighting schemes selected plausible matches for aligned preferences: Quiet Constellations for classical/relaxed/minimum energy and Ember Breaker for metal/intense/maximum energy. Formatting variations produced identical results. Unknown categories still allowed recommendations based on the remaining features, although this fallback does not establish that the results suit the listener.

## 6. Limitations and Bias

- **Catalog coverage:** Users whose tastes are absent or represented by one song have fewer matching choices. The model cannot recommend an opera song from this catalog. The extra lofi, pop, and indie pop entries create more opportunities for those genres to appear.
- **Handwritten category relationships:** Only pop and indie pop receive a related-genre bonus. Only chill, relaxed, and focused receive a related-mood bonus. These choices privilege particular relationships without evidence from listeners.
- **Weighting bias:** The original model can favor genre and mood despite a large energy mismatch. With ambient/chill/energy 1, Spacewalk Thoughts wins even though its energy is 0.28. Doubling energy narrows its lead but does not change that winner.
- **Tradeoffs from the weight shift:** Favoring energy closeness can reduce genre fidelity. For metal/relaxed/energy 0, Ember Breaker leaves the top five. For ambient/chill/energy 1, metal and intense-pop songs enter the top five. This is sensitivity to energy closeness, not a universal preference for high-energy music.
- **Unused preferences:** Turning `likes_acoustic` on or off has no effect, even though acousticness is available. Lyrics, language, artist preference, listening history, and other musical features are ignored. A single genre and mood cannot express mixed tastes or dislikes.
- **Input handling:** Blank and unknown categories silently fall back to other features. Out-of-range and nonfinite energies raise `ValueError`; missing energy raises `KeyError`, and text energy raises `TypeError`. The command-line app does not turn these exceptions into friendly guidance.
- **Ranking and evidence limits:** Lower IDs settle remaining ties without a taste-based reason. Scores are compatibility points, not probabilities or listener satisfaction. This small handpicked experiment cannot establish real-world accuracy or demographic fairness.

## 7. Evaluation

On October 31, 2026, the original model and a temporary in-memory variant were run on the same 18 profiles and 20-song catalog with five recommendations requested. The chosen experiment was **Weight Shift: halve genre importance and double energy importance**. Mood points and tie-breaking stayed unchanged; mood removal was not tested.

The comparison checked winners, ordered top-five lists, top-five membership, and exceptions. All 480 valid profile-song scores across the two variants were also checked against independently calculated component formulas. File hashes confirmed that `src/main.py` and `src/recommender.py` were unchanged after the experiment.

### Baseline and edge-case comparisons

Profiles below are written as genre / mood / energy. Each recommendation column lists the top three in rank order. **Original scores are out of 10; shifted scores are out of 11.** Raw score increases do not demonstrate improvement. To compare scores on a common scale, divide by the corresponding maximum; the conclusions here use rankings and membership.

| Profile | Original top three (score /10) | Weight-shift top three (score /11) | Effect across the top five |
|---|---|---|---|
| Baseline: pop / happy / 0.8 | Sunrise City (9.94); Rooftop Lights (7.88); Gym Hero (6.61) | Sunrise City (10.88); Rooftop Lights (9.76); Brass Boulevard (8.70) | Same five songs; Gym Hero falls from 3rd to 5th and Afterhours Steps rises from 5th to 4th. |
| Minimum energy: classical / relaxed / 0 | Quiet Constellations (9.64); Blue Velvet Hours (5.01); Coffee Shop Stories (4.89) | Quiet Constellations (10.28); Blue Velvet Hours (7.02); Coffee Shop Stories (6.78) | All five ranks unchanged. |
| Maximum energy: metal / intense / 1 | Ember Breaker (9.94); Gym Hero (5.79); Storm Runner (5.73) | Ember Breaker (10.88); Gym Hero (8.58); Storm Runner (8.46) | All five ranks unchanged. |
| Conflicting tastes: metal / relaxed / 0 | Quiet Constellations (5.64); Blue Velvet Hours (5.01); Coffee Shop Stories (4.89) | Quiet Constellations (8.28); Blue Velvet Hours (7.02); Coffee Shop Stories (6.78) | Ember Breaker leaves; Library Rain enters. Spacewalk Thoughts rises to 4th. |
| High-energy ambient: ambient / chill / 1 | Spacewalk Thoughts (7.84); Island Afternoon (4.59); Midnight Coding (4.26) | Spacewalk Thoughts (6.68); Island Afternoon (6.18); Ember Breaker (5.88) | Midnight Coding and Library Rain leave; Ember Breaker and Gym Hero enter. Concrete Verses remains 5th. |
| Unknown genre: opera / happy / 0.8 | Sunrise City (5.94); Rooftop Lights (5.88); Brass Boulevard (5.85) | Sunrise City (8.88); Rooftop Lights (8.76); Brass Boulevard (8.70) | All five ranks unchanged; no genre points available. |
| Unknown mood: pop / nostalgic / 0.8 | Sunrise City (6.94); Gym Hero (6.61); Rooftop Lights (4.88) | Sunrise City (7.88); Gym Hero (7.22); Rooftop Lights (6.76) | Paper Kite Goodbye leaves; Night Drive Loop enters. Brass Boulevard rises to 4th. |
| Both unknown: opera / nostalgic / 0.5 | Island Afternoon (2.91); Last Train Home (2.88); Paper Kite Goodbye (2.79) | Island Afternoon (5.82); Last Train Home (5.76); Paper Kite Goodbye (5.58) | All five ranks unchanged; doubling the only active component just doubles scores. |
| Blank labels: empty genre / empty mood / 0.5 | Island Afternoon (2.91); Last Train Home (2.88); Paper Kite Goodbye (2.79) | Island Afternoon (5.82); Last Train Home (5.76); Paper Kite Goodbye (5.58) | Same energy-only behavior as both unknown. |
| Formatting: `"  POP  "` / `" HAPPY "` / 0.8 | Same as original baseline | Same as shifted baseline | Normalization works under both schemes. |
| Acoustic preference on: baseline plus `likes_acoustic=True` | Same as original baseline | Same as shifted baseline | Acoustic preference is ignored. |
| Acoustic preference off: baseline plus `likes_acoustic=False` | Same as original baseline | Same as shifted baseline | Identical to preference on under each scheme. |

The remaining six profiles used the baseline genre and mood with the energy modifications below. Both schemes produced the same exceptions and no recommendation list.

| Energy modification | Original and shifted result |
|---|---|
| -0.1 | `ValueError`: preferred energy must be finite and between 0 and 1 |
| 1.1 | `ValueError`: preferred energy must be finite and between 0 and 1 |
| NaN | `ValueError`: preferred energy must be finite and between 0 and 1 |
| Positive infinity | `ValueError`: preferred energy must be finite and between 0 and 1 |
| Missing energy field | `KeyError: 'energy'` |
| Text value `"0.8"` | `TypeError`: must be real number, not str |

### Interpretation

Among the **12 valid profiles**, **0 winners changed**, **7 ordered top-five lists changed**, and **3 top-five memberships changed**. The 12 include three baseline-equivalent checks: formatting and the two acoustic settings. Excluding those repeats, 4 of 9 ordered lists changed and 3 of 9 memberships changed. These are descriptive counts for this selected set, not population-level estimates.

The baseline demonstrates why checking only the winner misses sensitivity: Sunrise City stays first, while Gym Hero drops two places. The conflicting and ambient profiles expose larger tradeoffs because songs enter and leave the list. For the ambient profile, the winner's lead over Island Afternoon shrinks from 3.25 to 0.50 points, while its energy remains far below the user's target.

The shift makes energy closeness more influential but does not address missing genres, ignored acoustic preferences, or input handling. There is no listener feedback showing that either weighting is better. The original weights remain the model's active configuration.

## 8. Future Work

- Validate all required preferences before scoring and explain blank or unsupported categories to the user.
- Evaluate an acoustic preference using the acousticness already in the catalog.
- Expand and balance the catalog, including currently absent genres, and support multiple likes and dislikes.
- Let users choose whether genre, mood, or energy matters most; evaluate those choices with listener feedback rather than selecting weights from intuition alone.
- Compare full recommendation lists and diversity, not just the first song, across a broader set of profiles.
- Complete the class-based API so it shares the functional scoring and explanations before presenting it as an alternative interface.

## 9. Personal Reflection

*Experiment-based reflection draft for personal adaptation:*

This experiment shows how recommendations reflect both the available songs and the importance assigned to each preference. Changing two weights left every tested winner unchanged, but altered several full lists. Looking only at the first recommendation would have hidden meaningful differences.

The ambient profile was particularly revealing: even after energy became more important, a low-energy song remained first because it matched both genre and mood. The acoustic comparison also shows why an available preference should not be assumed to influence the result. Clear explanations and targeted comparisons help reveal what a recommender actually uses, while real listener feedback is still needed to judge whether its suggestions are useful.
