# History Podcast Codex Skills

Codex skills for Chinese history/knowledge podcast production and WeChat article drafting.

## Workflows

### Podcast Audio Production

User-facing entrypoint:

```text
skills/podcast-series-showrunner/SKILL.md
```

It coordinates series planning, fixed spoken opening, episode brief, script, narration adaptation, TTS, and voice-only `episode.mp3` generation.

After the creative direction is approved, the showrunner must run a production readiness check before generating files or audio. It confirms the output folder, episode number, optional fact-check preference, and TTS credentials. API keys may be provided for the current run, but must never be written to project files or logs.

Writer skills are selected through `skills/writer_registry.json`. Current stable writer support is history; science, humanities, culture, travel, and business are registered as future extension points with fallback behavior.

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

It turns a completed `narration.txt` podcast narration into a WeChat Official Account draft. The narration can cover history, humanities, culture, science, social science, or other knowledge podcast topics.

Final successful output:

```text
article.html
image_manifest.json
images/
wechat_upload_result.json
```

Temporary machine files use `.wechat-work/` and are deleted after successful draft upload. The workflow does not produce intermediate Markdown.

Internal components:

```text
skills/wechat-history-article/
skills/wechat-image-director/
skills/wechat-html-publisher/
```

The WeChat workflow creates drafts only. It must not publish or mass-send.

WeChat credentials are read from environment variables or the local private file:

```text
~/.codex/wechat.env
```

Required:

```env
WECHAT_APPID=
WECHAT_APPSECRET=
```

Default author is `知识的小世界`; comments are enabled; content source URL is empty.

## Deterministic Tools

Run the audio half after `narration.txt`, `narration_meta.json`, and `opening_voice.wav` exist:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 tools/run_episode_pipeline.py \
  --series-dir /absolute/path/to/series \
  --episode-dir /absolute/path/to/series/episodes/ep01-title
```

Validate production outputs:

```bash
python3 tools/resolve_writer.py --validate
python3 tools/resolve_writer.py --domain science
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

The next planned evolution is to integrate the WeChat article workflow into the podcast showrunner flow. Once an episode narration is stable, a separate subagent can run `wechat-article-pipeline` while the main podcast workflow continues generating TTS and `episode.mp3`.

The goal is one coordinated production run that creates both:

- a listenable podcast episode
- a corresponding WeChat draft

Publishing and mass-send actions remain human-approved only.
