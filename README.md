# History Podcast Codex Skills

Codex skills for Chinese history/knowledge podcast production and WeChat article drafting.

## Workflows

### Podcast Audio Production

User-facing entrypoint:

```text
skills/podcast-series-showrunner/SKILL.md
```

It coordinates series planning, fixed spoken opening, episode brief, script, narration adaptation, TTS, and voice-only `episode.mp3` generation.

Stable internal skills:

```text
skills/podcast-series-opening-voice-producer/
skills/podcast-episode-director/
skills/history-script-writer/
skills/podcast-narration-adapter/
skills/podcast-tts-producer/
skills/podcast-episode-editor/
```

The audio pipeline produces:

```text
opening_voice.wav -> short silence -> voice.wav -> tail silence -> episode.mp3
```

It does not generate, choose, manage, or mix music or sound effects.

### WeChat Article Production

User-facing entrypoint:

```text
skills/wechat-article-pipeline/SKILL.md
```

It turns a podcast script, narration draft, article, or long-form source text into:

```text
article.json
image_manifest.json
images/
article.html
meta.json
WeChat Official Account draft
```

Internal components:

```text
skills/wechat-history-article/
skills/wechat-image-director/
skills/wechat-html-publisher/
```

The WeChat workflow creates drafts only. It must not publish or mass-send.

## Deterministic Tools

Run the audio half after `narration.txt`, `narration_meta.json`, and `opening_voice.wav` exist:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 tools/run_episode_pipeline.py \
  --series-dir /absolute/path/to/series \
  --episode-dir /absolute/path/to/series/episodes/ep01-title
```

Validate production outputs:

```bash
python3 tools/validate_production.py --series-dir /absolute/path/to/series
python3 tools/validate_production.py --episode-dir /absolute/path/to/series/episodes/ep01-title --strict
```

## Requirements

- Python 3.10+
- `ffmpeg` and `ffprobe` on `PATH`
- Python package `websockets`
- `DASHSCOPE_API_KEY` for CosyVoice TTS
- WeChat upload environment variables when creating drafts:
  - `WECHAT_APPID`
  - `WECHAT_APPSECRET`

Optional Python override:

```bash
export PODCAST_AUDIO_PYTHON=/path/to/python
```

## Future Direction

The next planned evolution is to integrate the WeChat article workflow into the podcast showrunner flow. Once an episode script or narration is stable, a separate subagent can run `wechat-article-pipeline` while the main podcast workflow continues generating TTS and `episode.mp3`.

The goal is one coordinated production run that creates both:

- a listenable podcast episode
- a corresponding WeChat draft

Publishing and mass-send actions remain human-approved only.
