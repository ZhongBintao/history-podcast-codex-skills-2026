# Podcast Codex Plugins

This repository packages Codex plugins for Chinese knowledge podcast production:

- `podcast-production`: plan a podcast series, write final episode narration, run CosyVoice TTS, and build a voice-only `episode.mp3`.
- `podcast-production-agent-version`: a subagent-first rewrite where `podcast-series-showrunner` creates one episode subagent per target episode and the main agent owns validation plus `production_state.json`.
- `wechat-article-production`: convert a completed `narration.txt` into a WeChat Official Account article draft.

The plugins are designed to be installed together from this repository, while still keeping the podcast and WeChat workflows separate.

## Repository Layout

```text
.agents/plugins/marketplace.json
plugins/
├── podcast-production/
│   ├── .codex-plugin/plugin.json
│   ├── skills/
│   │   ├── podcast-series-showrunner/
│   │   ├── history-script-writer/
│   │   ├── podcast-episode-director/
│   │   ├── podcast-tts-producer/
│   │   ├── podcast-episode-editor/
│   │   ├── podcast-series-opening-voice-producer/
│   │   └── writer_registry.json
│   └── scripts/
│       ├── resolve_writer.py
│       ├── run_episode_pipeline.py
│       ├── robust_episode_tts.py
│       └── validate_production.py
├── podcast-production-agent-version/
│   ├── .codex-plugin/plugin.json
│   ├── README.md
│   ├── skills/
│   │   └── podcast-series-showrunner/
│   └── scripts/
│       ├── build_episode.py
│       ├── cosyvoice_ws_tts.py
│       ├── run_episode_pipeline.py
│       ├── robust_episode_tts.py
│       └── validate_production.py
└── wechat-article-production/
    ├── .codex-plugin/plugin.json
    └── skills/
        ├── wechat-article-pipeline/
        ├── wechat-narration-article/
        ├── wechat-image-director/
        └── wechat-html-publisher/
```

## How A New User Uses This

1. Give the user this repository URL:

   ```text
   https://github.com/ZhongBintao/podcast-skills
   ```

2. The user installs the repository as a Codex plugin source. Codex reads `.agents/plugins/marketplace.json` and exposes three installable plugins:

   - `Podcast Production`
   - `Podcast Production Agent Version`
   - `WeChat Article Production`

3. For podcast creation, start with:

   ```text
   Use podcast-series-showrunner to plan a Chinese history podcast series.
   ```

   The showrunner is the only user-facing podcast entrypoint. It clarifies the idea, proposes directions, asks for production readiness, then orchestrates the internal skills.

   For the subagent-first version, start with:

   ```text
   Use podcast-series-showrunner from podcast-production-agent-version to plan a podcast series.
   ```

   After the season plan is confirmed, ask it to generate target episodes. It will create one subagent task packet per episode, validate the returned outputs, and update `production_state.json` itself.

4. For WeChat article creation, start with:

   ```text
   Use wechat-article-pipeline to turn this narration.txt into a WeChat draft.
   ```

   The WeChat workflow creates a draft only. It must not publish or mass-send.

## Podcast Workflow

User-facing entrypoint:

```text
plugins/podcast-production/skills/podcast-series-showrunner/
```

Internal components:

```text
podcast-series-opening-voice-producer
podcast-episode-director
history-script-writer
podcast-tts-producer
podcast-episode-editor
```

Default model-produced flow:

```text
series_plan.json
→ episode_brief.json
→ narration.txt + fact_check.md(optional)
```

Script/API-produced flow:

```text
voice.wav
→ voice_timeline_raw.json
→ voice_timeline_compact.json
→ tts_manifest.json
→ episode.mp3
→ production_manifest.json
→ production_state.json update
```

The audio workflow produces a complete voice-only episode:

```text
opening_voice.wav -> short silence -> voice.wav -> tail silence -> episode.mp3
```

It does not create music, sound effects, or a final mixed music version.

## Podcast Agent-Version Workflow

User-facing entrypoint:

```text
plugins/podcast-production-agent-version/skills/podcast-series-showrunner/
```

Default flow:

```text
showrunner confirms series plan and opening voice
→ main agent checks series_dir, target episodes, opening_voice.wav, scripts, and DASHSCOPE_API_KEY
→ main agent creates one subagent task packet per episode
→ each subagent writes only its episode_dir
→ main agent validates episode_brief.json, narration.txt, TTS outputs, episode.mp3, and manifests
→ main agent updates production_state.json
```

Episode subagents use direct scripts:

```text
scripts/cosyvoice_ws_tts.py
scripts/build_episode.py
scripts/validate_production.py
```

`scripts/run_episode_pipeline.py` is retained for main-agent controlled runs because it writes `production_state.json`.

Before producing audio, the showrunner must confirm:

- output series folder
- episode number or range
- whether to force `fact_check.md`
- `DASHSCOPE_API_KEY` for CosyVoice TTS

API keys may be provided for one run, but must never be written to project files, manifests, Markdown, logs, or final replies.

## WeChat Article Workflow

User-facing entrypoint:

```text
plugins/wechat-article-production/skills/wechat-article-pipeline/
```

Internal components:

```text
wechat-narration-article
wechat-image-director
wechat-html-publisher
```

Default flow:

```text
narration.txt
→ .wechat-work/article.json
→ images/ + image_manifest.json
→ article.html
→ WeChat draft
```

Final successful output:

```text
article.html
image_manifest.json
images/
wechat_upload_result.json
```

WeChat credentials are read from environment variables first, then from:

```text
~/.codex/wechat.env
```

Required:

```env
WECHAT_APPID=
WECHAT_APPSECRET=
```

Defaults:

```env
WECHAT_AUTHOR=知识的小世界
WECHAT_CONTENT_SOURCE_URL=
WECHAT_NEED_OPEN_COMMENT=1
WECHAT_ONLY_FANS_CAN_COMMENT=0
```

## Deterministic Commands

Run from the podcast plugin root:

```bash
cd plugins/podcast-production
```

Validate writer routing:

```bash
python3 scripts/resolve_writer.py --validate
python3 scripts/resolve_writer.py --domain history
python3 scripts/resolve_writer.py --domain science
```

Run the deterministic audio half after `narration.txt` and `opening_voice.wav` exist:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 scripts/run_episode_pipeline.py \
  --series-dir /absolute/path/to/series \
  --episode-dir /absolute/path/to/series/episodes/ep01-title
```

Validate production outputs:

```bash
python3 scripts/validate_production.py --series-dir /absolute/path/to/series
python3 scripts/validate_production.py --episode-dir /absolute/path/to/series/episodes/ep01-title --strict
```

## Requirements

- Python 3.10+
- `ffmpeg` and `ffprobe` on `PATH`
- Python package `websockets`
- `DASHSCOPE_API_KEY` for CosyVoice TTS
- WeChat draft credentials when using the WeChat plugin:
  - `WECHAT_APPID`
  - `WECHAT_APPSECRET`

Optional Python override:

```bash
export PODCAST_AUDIO_PYTHON=/path/to/python
```

## Adding Future Writer Skills

`history-script-writer` is the first writer implementation, not the hard-coded center of the workflow.

Future domains should be added as sibling writer skills inside:

```text
plugins/podcast-production/skills/
```

Examples:

```text
science-script-writer/
humanities-script-writer/
culture-script-writer/
```

Every writer skill must follow the same minimum contract:

```text
Input: episode_brief.json
Required output: narration.txt
Optional output: fact_check.md
Do not create audio, timestamps, music, sound-effect notes, manifests, or final mix files.
```

To upgrade the plugin with a new writer:

1. Create `plugins/podcast-production/skills/<domain>-script-writer/SKILL.md`.
2. Add `agents/openai.yaml` and set `allow_implicit_invocation: false`, because writers are internal modules.
3. Update `plugins/podcast-production/skills/writer_registry.json`:
   - set the domain's `skill` to the new writer skill name
   - set `available: true`
   - keep `required_inputs: ["episode_brief.json"]`
   - keep `default_outputs: ["narration.txt"]`
   - set a clear `fact_check_policy`
4. Run:

   ```bash
   cd plugins/podcast-production
   python3 scripts/resolve_writer.py --validate
   python3 scripts/resolve_writer.py --domain science
   ```

5. Test one full planning run through `podcast-series-showrunner` and confirm `episode_brief.json.recommended_writer_skill` points to the new writer.

Because downstream tools consume `narration.txt`, adding a new writer should not require changes to TTS, editing, or the WeChat article plugin.
