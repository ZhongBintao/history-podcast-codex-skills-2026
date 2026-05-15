---
name: history-script-writer
description: 内部模块：历史文化播客写稿。Normally invoked by podcast-series-showrunner after episode_brief.json is created. Produces narration.txt by default, with optional fact_check.md for high-risk or explicitly required episodes. Do not expose as the default user-facing entrypoint.
---

# History Script Writer

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Write the final spoken narration for a historical or history-culture podcast episode from `episode_brief.json`. `narration.txt` is both the human-reviewable master text and the TTS input.

Create a separate `fact_check.md` only when the brief marks fact checking as required, the topic is disputed/high-risk, or the user explicitly asks.

Keep this skill focused on spoken content. Leave audio, timestamps, editing, manifests, and final mixing to downstream production tools.

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
- `historical_anchors`
- `emotional_arc`
- `host_persona`
- `voice_direction`
- `domain_constraints`
- `fact_check_requirements`
- `avoid`

If the brief is not historical or does not recommend `history-script-writer`, check `writer_fallback_reason`. If this skill was selected as a registry fallback, continue as a general spoken-narration writer while preserving the brief's domain constraints. Otherwise say so briefly and ask whether to continue.

## Writer Extension Contract

This skill is one implementation of the shared writer contract. Future science, humanities, culture, travel, or business writers must keep the same minimum interface:

- Input: `episode_brief.json`.
- Required output: `narration.txt`.
- Optional output: `fact_check.md`.
- Do not create audio, timestamps, music, sound-effect notes, manifests, or final mix files.
- Respect `fact_check_requirements.required` and create `fact_check.md` only when required by the brief, topic risk, or user request.

The writer selected in `episode_brief.json.recommended_writer_skill` comes from `skills/writer_registry.json`. Do not hard-code new domain routing inside this skill.

## Outputs

Write the outputs beside `episode_brief.json` unless the user specifies another folder:

```text
narration.txt
fact_check.md optional
```

## Workflow

1. Parse `episode_brief.json`.
2. Confirm the task is historical or history-culture, or that this writer is being used as the selected fallback.
3. Extract the core question, narrative angle, modules, anchors, voice persona, and avoid rules.
4. Gather or verify historical facts when the brief requires fact checking. For unstable, disputed, niche, or easily misremembered claims, use reliable sources instead of memory.
5. Draft `narration.txt` as final spoken Chinese narration, shaped around the brief's structure and emotional arc.
6. If fact checking is required, draft a concise `fact_check.md` as production-only verification notes. Mark only important claims as supported, interpretive, uncertain, or needs review.

## Narration Style

Write in Chinese for a spoken podcast host.

Follow the host persona:

- Curious, restrained, and clear.
- Like sharing a serious discovery with a friend.
- Avoid marketing tone, sensationalism, and internet gag cadence.

The narration should:

- Answer the `core_question`.
- Follow `narrative_angle`.
- Use the requested `structure` without visible headings.
- Keep paragraphs readable for human review and suitable for direct TTS.
- Prefer concrete scenes, mechanisms, and evidence over vague atmosphere.
- Clearly separate known facts, archaeological interpretation, colonial textual accounts, and modern scholarly debate.
- Keep the target length close to `target_length_chars` when feasible. A draft may be shorter for testing, but production should aim near the target.

## Opening Craft

The first spoken paragraph must be a crafted cold open, not a reusable template. Do not default to broad topic framing.

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

The opening may be quiet, but it must have narrative tension. It should make the listener feel "I had not looked at it this way," without sounding like a short-video hook. Vary openings across episodes in the same series; never reuse the same sentence skeleton.

## Narration Cleanliness

`narration.txt` must be pure spoken text:

- Use paragraphs separated by blank lines.
- Do not include Markdown headings, bullet lists, tables, links, footnotes, timestamps, emotion tags, pronunciation tags, SSML, source notes, or production comments.
- Do not include fact-check notes in the spoken body.
- Do not include music, sound-effect, or editing directions.
- Keep punctuation natural for Chinese TTS.

## Fact Check

Write `fact_check.md` for the production team, not for broadcast, only when it is needed.

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

## Quality Checklist

Before finishing:

- Confirm `narration.txt` exists.
- Confirm `narration.txt` follows the brief and is clean spoken text.
- If `fact_check.md` is created, confirm it is separate from the narration.
- Confirm historical uncertainty is marked in the narration or fact-check notes instead of smoothed over.
