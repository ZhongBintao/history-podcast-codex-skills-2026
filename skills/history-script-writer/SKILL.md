---
name: history-script-writer
description: 内部模块：历史文化播客写稿。Normally invoked by podcast-series-showrunner after episode_brief.json is created. Produces script_full.md, fact_check.md, and script_meta.json. Do not expose as the default user-facing entrypoint.
---

# History Script Writer

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Write the full draft script for a historical or history-culture podcast episode from `episode_brief.json`. Produce human-reviewable prose and a separate fact-check file for the production team.

Keep this skill focused on content writing. Leave clean TTS narration, sound-effect marks, timestamps, audio, and final mixing to downstream skills.

## Inputs

Require:

- `episode_brief.json`

Use these fields when present:

- `series_name`
- `episode_no`
- `episode_title`
- `target_length_chars`
- `core_question`
- `narrative_angle`
- `structure`
- `content_modules`
- `knowledge_anchors`
- `emotional_arc`
- `host_persona`
- `domain_constraints`
- `fact_check_requirements`
- `avoid`

If the brief is not historical or does not recommend `history-script-writer`, say so briefly and either stop or ask whether to continue as a custom history-culture draft.

## Outputs

Write the outputs beside `episode_brief.json` unless the user specifies another folder:

```text
script_full.md
fact_check.md
script_meta.json
```

## Workflow

1. Parse `episode_brief.json`.
2. Confirm the task is historical or history-culture.
3. Extract the core question, narrative angle, modules, anchors, voice persona, and avoid rules.
4. Gather or verify historical facts when the brief requires fact checking. For unstable, disputed, niche, or easily misremembered claims, use reliable sources instead of memory.
5. Draft `script_full.md` around the brief's structure and emotional arc.
6. Draft `fact_check.md` as production-only verification notes. Mark each important claim as supported, interpretive, uncertain, or needs review.
7. Draft `script_meta.json` with paths, character counts, source brief, and status.
8. Validate `script_meta.json` as parseable JSON.

## Script Style

Write in Chinese for a spoken podcast host.

Follow the host persona:

- Curious, restrained, and clear.
- Like sharing a serious discovery with a friend.
- Avoid marketing tone, sensationalism, and internet gag cadence.

The script should:

- Answer the `core_question`.
- Follow `narrative_angle`.
- Use the requested `structure` without making section transitions stiff.
- Keep paragraphs readable for human review.
- Prefer concrete scenes, mechanisms, and evidence over vague atmosphere.
- Clearly separate known facts, archaeological interpretation, colonial textual accounts, and modern scholarly debate.
- Keep the target length close to `target_length_chars` when feasible. A draft may be shorter for testing, but production should aim near the target.

## Opening Craft

The first spoken paragraph must be written as a crafted cold open, not a reusable template. Do not default to broad topic framing.

Avoid formulaic openings such as:

- `如果我们今天说到...`
- `提到...，很多人会想到...`
- `在历史的长河中...`
- `这是一座/一个...的...`
- `今天我们要聊...`
- direct encyclopedia-style definition

Choose one concrete entry instead:

- a physical detail: stone, water, road, wall, inscription, harbor, tool, document
- a spatial contradiction: a small hill becomes a symbolic center; a marginal road becomes an imperial route
- a dated rupture: a siege, fire, exile, discovery, law, trial, voyage, or excavation
- a human action visible in the scene: carrying water, walking a route, copying a text, rebuilding a gate
- a precise question that unsettles the obvious answer

The opening may be quiet, but it must have narrative tension. It should make the listener feel “I had not looked at it this way,” without sounding like a short-video hook. Vary openings across episodes in the same series; never reuse the same sentence skeleton.

The script may include Markdown headings for review, for example:

```markdown
# 第 1 集：雨林里的时间机器

## 反常识开场

...
```

Do not include:

- TTS pronunciation tags.
- Emotion tags such as `[calm]`.
- Sound-effect labels.
- Timestamp guesses.
- Fact-check notes inside the spoken body.
- Internal production comments inside the spoken body.

## Fact Check

Write `fact_check.md` for the production team, not for broadcast.

Include:

- Source brief path.
- Main claims checklist.
- Terms and names that need pronunciation or translation review.
- Uncertainties and disputed points.
- Source list with URLs or bibliographic notes when available.
- Items that should not be overstated in the final narration.

Use claim statuses:

```text
supported
interpretive
uncertain
needs_review
```

For history topics, be especially careful with:

- Archaeological interpretation versus direct evidence.
- Colonial-era written accounts and their bias.
- Dates and period names.
- Claims about religion, ritual, violence, decline, or disappearance.
- Comparisons across civilizations.

## Metadata

Write `script_meta.json` with this shape:

```json
{
  "series_name": "太阳、雨林与高原",
  "episode_no": 1,
  "episode_title": "雨林里的时间机器",
  "writer_skill": "history-script-writer",
  "target_length_chars": 5000,
  "actual_length_chars": 5120,
  "source_brief": "/absolute/path/to/episode_brief.json",
  "script_full_path": "/absolute/path/to/script_full.md",
  "fact_check_path": "/absolute/path/to/fact_check.md",
  "status": "draft",
  "next_step": {
    "target_skill": "podcast-narration-adapter",
    "expected_outputs": ["narration.txt", "narration_meta.json"]
  }
}
```

Count `actual_length_chars` for the spoken draft body, excluding the fact-check file. It may include Markdown headings if the file is still in review form.

## Quality Checklist

Before finishing:

- Confirm the three output files exist.
- Confirm `script_full.md` follows the brief and does not contain sound-effect or TTS tags.
- Confirm `fact_check.md` is separate from the script.
- Confirm `script_meta.json` is valid JSON and uses absolute paths.
- Confirm historical uncertainty is marked instead of smoothed over.
- Confirm the next step points to `podcast-narration-adapter`.
