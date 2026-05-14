---
name: podcast-narration-adapter
description: 内部模块：播客口播适配。Normally invoked by podcast-series-showrunner after script_full.md and fact_check.md are created. Produces clean TTS-only narration.txt plus narration_meta.json. Do not expose as the default user-facing entrypoint.
---

# Podcast Narration Adapter

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Convert a reviewed podcast script into clean narration text for TTS, plus machine-readable paragraph metadata.

## Current MVP Boundary

- Do create: `narration.txt` and `narration_meta.json`.
- Do clean: Markdown headings, review formatting, footnotes, fact-check notes, and internal comments.
- Do adapt: long sentences, awkward written phrasing, numerals, years, ranges, foreign names, and paragraph rhythm for spoken delivery.
- Do prepend: a short fixed re-entry line before the episode body, default `好的，欢迎回到这期节目。`
- Do append: a restrained fixed closing line as the final paragraph unless the user defines another closing line.
- Do not create: `voice.wav`, timestamps, sound files, music plans, sound-effect notes, final cue decisions, or final mixes.
- Do not put sound marks, model emotion tags, source notes, or fact-check notes in `narration.txt`.

## Inputs

```text
episode_brief.json
script_full.md
fact_check.md
```

Use `fact_check.md` only to avoid overstating disputed or uncertain claims. Do not copy fact-check content into narration.

## Outputs

```text
narration.txt
narration_meta.json
```

Write beside `script_full.md` unless the user specifies another folder.

## Workflow

1. Parse `episode_brief.json`.
2. Read `script_full.md` and remove Markdown structure from the TTS body.
3. Check `fact_check.md` for cautions about uncertainty, names, dates, and pronunciation.
4. Rewrite only where useful for oral delivery: split overlong sentences, remove visual Markdown transitions, normalize numbers and years, clarify foreign names, and keep host persona intact.
5. Create `narration.txt` as plain text paragraphs.
6. Prepend the default re-entry line as the first paragraph: `好的，欢迎回到这期节目。`
7. Append the default closing line as the final paragraph: `好，这一期就先到这里。我们下期再见。`
8. Create `narration_meta.json` with stable paragraph IDs.
9. Validate JSON and confirm metadata text exactly matches `narration.txt`.

## Narration Rules

`narration.txt` must be pure text for TTS:

- No Markdown headings or bullets.
- No `#`, `*`, table syntax, links, or code fences.
- No fact-check notes.
- No sound-effect tags.
- No model labels such as `[calm]`, `[pause]`, or `<emotion>`.
- No timestamps or guessed seconds.
- No internal comments.

Keep paragraphs short enough for stable TTS. Prefer one spoken idea per paragraph. Preserve a blank line between paragraphs.

## Metadata

Write `narration_meta.json` like this:

```json
{
  "series_name": "穿过欧亚的路",
  "episode_no": 1,
  "episode_title": "不是一条路",
  "source_script": "/absolute/path/to/script_full.md",
  "source_brief": "/absolute/path/to/episode_brief.json",
  "paragraphs": [
    {
      "id": "p001",
      "text": "好的，欢迎回到这期节目。",
      "char_count": 12,
      "role": "body_intro"
    },
    {
      "id": "p002",
      "text": "如果我们把丝绸之路想成地图上的一条线，很容易从一开始就误会它。",
      "char_count": 34,
      "role": "body"
    },
    {
      "id": "p069",
      "text": "好，这一期就先到这里。我们下期再见。",
      "char_count": 18,
      "role": "outro_voice"
    }
  ],
  "tts_notes": {
    "preferred_pace": "medium_slow",
    "tone": "克制、清晰、口语化但不过度娱乐，像和朋友分享一个认真发现",
    "do_not_add_emotion_tags": true
  },
  "closing_line": {
    "enabled": true,
    "text": "好，这一期就先到这里。我们下期再见。"
  },
  "body_intro_line": {
    "enabled": true,
    "text": "好的，欢迎回到这期节目。"
  },
  "next_step": {
    "target_skill": "podcast-tts-producer",
    "expected_outputs": ["voice.wav", "voice_timeline_raw.json", "voice_timeline_compact.json", "tts_manifest.json"]
  }
}
```

## Quality Checklist

- `narration.txt` has no Markdown, tags, timestamps, or fact-check material.
- Every `narration_meta.json.paragraphs[].text` exactly appears in `narration.txt`.
- The final closing line is present and marked `outro_voice`.
- No sound-effect marker file is generated for the stable MVP.
- Next step points to `podcast-tts-producer`.
