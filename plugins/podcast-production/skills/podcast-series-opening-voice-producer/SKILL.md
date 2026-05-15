---
name: podcast-series-opening-voice-producer
description: 内部模块：播客系列固定片头口播生产。Normally invoked by podcast-series-showrunner after the opening voice text has been approved in the showrunner conversation. Saves series_opening_voice.md/json and synthesizes opening_voice.wav. Do not expose as the default user-facing entrypoint.
---

# Podcast Series Opening Voice Producer

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Create the fixed spoken opening audio for a podcast series from text already approved in the `podcast-series-showrunner` conversation. The opening is a reusable voice asset, not a music bed and not a final mixed intro.

## Current MVP Boundary

- Do create: `series_opening_voice.md`, `series_opening_voice.json`, `opening_voice.wav`, and `opening_voice_tts_manifest.json`.
- Do use: `series_plan.json` and `DASHSCOPE_API_KEY`.
- Do not run a separate user-facing approval round; approval happens in `podcast-series-showrunner`.
- Do not create: music, sound effects, final episode audio, or mixed intro/outro assets.
- Do not mention music, sound effects, or editing instructions in the opening copy.
- Do not write API keys into files.

## Inputs

```text
series_plan.json
```

## Outputs

```text
series_opening_voice.md
series_opening_voice.json
opening_voice.wav
opening_voice_tts_manifest.json
```

## Workflow

1. Parse `series_plan.json`.
2. Read `series_name`, `series_logline`, `selected_direction`, `global_style.voice_identity`, `global_style.host_persona`, and `opening_voice`.
3. Read the approved `opening_voice.selected_text`. If it is missing, stop and route back to `podcast-series-showrunner`.
4. Write `series_opening_voice.md` for traceability.
5. Write `series_opening_voice.json` with selected text, style, source path, output path, and manifest path.
6. Create a minimal temporary narration meta for the selected opening text, or use the TTS producer script with an opening-specific prefix.
7. Call CosyVoice with `word_timestamp_enabled=true` and save `opening_voice.wav`, `opening_voice_timeline_raw.json`, `opening_voice_timeline_compact.json`, and `opening_voice_tts_manifest.json`.
8. Validate JSON and confirm `opening_voice.wav` is non-empty.

## Opening Copy Rules

- It should identify the series quickly.
- It should create a macro frame and listening promise with real imagery, not generic words.
- It should be reusable across all episodes.
- It may be cinematic, but must stay restrained.
- Avoid advertising slogans, course-sales phrasing, short-video hooks, and exaggerated suspense.
- Do not bind the copy to one episode.
- Do not mention music, sound effects, or editing.
- Do not simply list keywords from `series_plan.json`; transform them into a coherent series-level sentence.
- Avoid weak scaffolding such as `我们从A、B、C出发，走进...` unless the rhythm is unusually strong.
- Prefer an image or conceptual movement that can carry the whole season.
- The copy should feel like the doorway to a serious documentary podcast: spacious, memorable, and precise.

## Opening Voice Quality Bar

Before selecting a candidate, score it against these questions:

- Does it say why this series exists, beyond naming the topic?
- Does it contain at least one concrete image or spatial idea?
- Can it survive being heard before every episode without sounding repetitive or promotional?
- Does it avoid empty grandeur such as `时间深处`, `文明密码`, `历史长河`, unless the phrase is made specific by context?
- Would a human editor keep it after hearing it three times?

Reject candidates that are merely a polished summary of keywords.

## JSON Shape

```json
{
  "series_name": "穿过欧亚的路",
  "selected_text": "这里是《穿过欧亚的路》。我们从一条条商道、一个个绿洲和一座座帝国边境出发，重新看见文明如何在漫长的迁徙、交易与相遇中改变彼此。",
  "target_duration_sec": "15-30",
  "style": "宏观、克制、有代入感、非广告腔",
  "source_series_plan": "/absolute/path/to/series_plan.json",
  "output_audio": "/absolute/path/to/opening_voice.wav",
  "tts_manifest": "/absolute/path/to/opening_voice_tts_manifest.json",
  "selection_reason": "主题识别清楚，足够长期复用，不绑定单集。",
  "policy": "Fixed series opening voice only; no music, sound effects, or final mixing."
}
```

## TTS Command

Use the bundled TTS script from `podcast-tts-producer`:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 skills/podcast-tts-producer/scripts/cosyvoice_ws_tts.py \
  --narration /absolute/path/to/opening_voice_narration.txt \
  --out-dir /absolute/path/to/series-folder \
  --output-prefix opening_voice \
  --manifest-name opening_voice_tts_manifest.json \
  --model cosyvoice-v3-flash \
  --voice longsanshu_v3 \
  --max-chars-per-task 700
```

The temporary `opening_voice_narration.txt` may remain in the folder as a traceable TTS input.

## Quality Checklist

- `series_opening_voice.json` is valid JSON.
- Opening text contains no music, sound-effect, or editing instruction.
- `opening_voice.wav` exists and is non-empty.
- `opening_voice_tts_manifest.json` has `api_key_source`, never the real key.
- The next production step is `podcast-episode-director`.
