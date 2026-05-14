---
name: podcast-episode-editor
description: 内部模块：播客单集口播版剪辑。Normally invoked by podcast-series-showrunner after opening_voice.wav and voice.wav are ready. Combines fixed opening voice and body narration into complete spoken episode.mp3. Do not expose as the default user-facing entrypoint.
---

# Podcast Episode Editor

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Create the complete spoken episode MP3 by joining:

```text
opening_voice.wav -> short silence -> voice.wav -> tail silence
```

This is the AI-produced complete spoken version. It is directly listenable and presentable as a full voice-only episode. Human post-production may later add opening music, ending music, background music, sound effects, or aesthetic mastering, but those are outside this skill.

## Boundary

- Do create: `episode.mp3` and `production_manifest.json`.
- Do use: `opening_voice.wav`, `voice.wav`, and optional timeline manifests for metadata only.
- Do not create or add: music, background music, sound effects, final music mix, or guessed timestamps.
- Do not require any historical intro/outro mix manifest or mixed music assets.
- Do not create a separate audio-splicing skill; concatenation belongs here.

## Inputs

Require:

```text
opening_voice.wav
voice.wav
```

Optional:

```text
voice_timeline_compact.json
opening_voice_timeline_compact.json
episode_slug
```

## Outputs

Write beside `voice.wav` unless the user specifies another output folder:

```text
episode.mp3
production_manifest.json
```

## Bundled Script

Use the bundled script:

```bash
python3 skills/podcast-episode-editor/scripts/build_episode.py \
  --opening-voice /absolute/path/to/opening_voice.wav \
  --voice /absolute/path/to/voice.wav \
  --out-dir /absolute/path/to/series-folder \
  --episode-slug episode
```

Optional timeline metadata:

```bash
python3 skills/podcast-episode-editor/scripts/build_episode.py \
  --opening-voice /absolute/path/to/opening_voice.wav \
  --voice /absolute/path/to/voice.wav \
  --opening-timeline /absolute/path/to/opening_voice_timeline_compact.json \
  --voice-timeline /absolute/path/to/voice_timeline_compact.json \
  --out-dir /absolute/path/to/series-folder
```

The script requires `ffmpeg` and `ffprobe` on PATH.

## Editing Rules

- Preserve both source voice files exactly in order.
- Default silence after opening voice: `1.2` seconds.
- Default tail silence after body: `1.0` seconds.
- Export MP3 only, default `192k`.
- Apply gentle loudness normalization to the complete voice-only episode.
- Record generated paths, durations, and commands in `production_manifest.json`.
- Mark music and sound effects as absent by design.

## Manifest Rules

`production_manifest.json` should include:

```json
{
  "episode_audio_mp3": "/absolute/path/to/episode.mp3",
  "inputs": {
    "opening_voice": "/absolute/path/to/opening_voice.wav",
    "voice": "/absolute/path/to/voice.wav"
  },
  "edit_scope": {
    "complete_spoken_episode": true,
    "opening_voice": true,
    "body_voice": true,
    "music": false,
    "sound_effects": false,
    "final_music_mix": false
  },
  "failed_reason": null
}
```

If generation fails, write `production_manifest.json` with `failed_reason` and do not create fake audio.

## Quality Checklist

- `episode.mp3` exists and is non-empty.
- `production_manifest.json` is valid JSON and uses absolute paths.
- The file sequence is opening voice, silence, body voice, tail silence.
- Music and sound effects are marked false.
- No separate splicing skill is required.
