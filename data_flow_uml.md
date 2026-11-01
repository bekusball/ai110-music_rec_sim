# Recommendation data flow

Planned logic from [plan.log](plan.log), shown as a UML activity-style diagram using Mermaid.

```mermaid
flowchart TD
    input["Input: user preferences<br/>pop, happy, energy 0.80; k = 5"] --> load["Load songs from CSV"]
    load --> loop{"Another song?"}
    loop -- Yes --> score["Score this song<br/>Genre + mood + energy = score out of 10"]
    score --> save["Save song, score, and explanation"]
    save --> loop
    loop -- No --> rank["Rank all songs by score<br/>Break ties by closer energy, then lower ID"]
    rank --> output["Output: Top K recommendations<br/>Songs with scores and explanations"]
```

Every song is scored before selecting the top K. Scoring rules, validation, and empty-input behavior are defined in `plan.log`.
