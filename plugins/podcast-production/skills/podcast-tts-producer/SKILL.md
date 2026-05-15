---
name: podcast-tts-producer
description: 内部模块：播客TTS生产。Normally invoked by podcast-series-showrunner for opening voice and episode narration. Calls DashScope CosyVoice WebSocket TTS and outputs audio, timelines, and TTS manifests. Do not expose as the default user-facing entrypoint.
---

# Podcast TTS Producer

Internal module. Normal users should enter through `podcast-series-showrunner`.

## Role

Call CosyVoice TTS with clean narration text and save the resulting voice audio plus real timestamp handoff files.

This is the first step that contacts a paid/external TTS API. Treat credentials, cost, retries, and manifests carefully.

## Boundary

- Do create: `voice.wav`, `voice_timeline_raw.json`, `voice_timeline_compact.json`, and `tts_manifest.json`.
- Do use: `narration.txt` and environment variable `DASHSCOPE_API_KEY`.
- Do not create: sound effects, context packets for effects, final episode mix, intro/outro assets, or publishing files.
- Do not estimate timestamps. Use only timestamps returned by the TTS API.
- Do not write API keys into scripts, manifests, logs, Markdown, or terminal output.

## Default TTS

For episode body narration, use one direct CosyVoice WebSocket task by default:

```text
body_generation_mode: single_task
body_script: skills/podcast-tts-producer/scripts/cosyvoice_ws_tts.py
body_max_chars_per_task: 10000
fallback_body_script: scripts/robust_episode_tts.py
```

For short fixed series opening voice, use the lower-level WebSocket script directly:

```text
model: cosyvoice-v3-flash
voice: longsanshu_v3
api: Alibaba Cloud Model Studio / DashScope CosyVoice WebSocket API
endpoint: wss://dashscope.aliyuncs.com/api-ws/v1/inference/
audio_format: wav
sample_rate: 24000
word_timestamp_enabled: true
opening_generation_mode: single_task
send_mode: combined
max_chars_per_task: 10000
chunk_silence_ms: 0
tail_silence_ms: 3500
```

Official behavior to preserve:

- WebSocket authentication uses `Authorization: bearer <api_key>`.
- Use one WebSocket task for normal episode bodies. The pipeline assumes episodes are usually under 5000 Chinese characters.
- The script derives paragraph IDs from blank-line-separated paragraphs in `narration.txt`.
- For the task, send `run-task`, then one combined `continue-task` text containing the whole narration, then `finish-task`.
- Enable `word_timestamp_enabled` in `parameters`.
- Save timestamp data from `result-generated` events.
- Save binary audio exactly as received and append tail silence locally.

## Scripts

Use the low-level bundled script for short text or individual worker chunks:

```text
skills/podcast-tts-producer/scripts/cosyvoice_ws_tts.py
```

Typical command:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 skills/podcast-tts-producer/scripts/cosyvoice_ws_tts.py \
  --narration /absolute/path/to/narration.txt \
  --out-dir /absolute/path/to/output-dir \
  --output-prefix voice \
  --manifest-name tts_manifest.json \
  --model cosyvoice-v3-flash \
  --voice longsanshu_v3 \
  --send-mode combined \
  --max-chars-per-task 10000 \
  --chunk-silence-ms 0 \
  --tail-silence-ms 3500
```

The script requires the Python package `websockets`. If missing, install it in a local or temporary environment, not by editing this skill.

If direct TTS repeatedly fails because of network instability, the fallback is the robust orchestration script:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 scripts/robust_episode_tts.py \
  --narration /absolute/path/to/narration.txt \
  --out-dir /absolute/path/to/episode-dir \
  --output-prefix voice \
  --manifest-name tts_manifest.json \
  --model cosyvoice-v3-flash \
  --voice longsanshu_v3 \
  --max-chars-per-task 300 \
  --chunk-silence-ms 450 \
  --tail-silence-ms 3500 \
  --retries 2
```

The robust script calls the low-level TTS script once per external chunk. Completed chunks are reusable, but this path costs more orchestration and creates more handoff files, so do not use it by default.

## Inputs

Require:

```text
narration.txt
```

Optional:

```text
DASHSCOPE_WORKSPACE
```

Use `DASHSCOPE_WORKSPACE` only as a WebSocket header when the user or environment provides it. Do not write it into logs unless required for debugging, and never write API keys.

## Outputs

Write beside `narration.txt` unless the user specifies another folder:

```text
voice.wav
voice_timeline_raw.json
voice_timeline_compact.json
tts_manifest.json
voice_chunks/
```

For robust fallback generation, chunk work files live under:

```text
voice_robust_chunks/
```

For fixed series opening voice, callers may pass `--output-prefix opening_voice --manifest-name opening_voice_tts_manifest.json`, which produces:

```text
opening_voice.wav
opening_voice_timeline_raw.json
opening_voice_timeline_compact.json
opening_voice_tts_manifest.json
opening_voice_chunks/
```

If the API call fails, still write `tts_manifest.json` with `failed_reason`, but do not create fake audio or fake timestamps.

## Manifest Rules

`tts_manifest.json` must include:

```json
{
  "model": "cosyvoice-v3-flash",
  "voice": "longsanshu_v3",
  "api_type": "websocket",
  "generation_mode": "single_task",
  "send_mode": "combined",
  "max_chars_per_task": 10000,
  "chunk_silence_ms": 0,
  "tail_silence_ms": 3500,
  "word_timestamp_enabled": true,
  "input_chars": 4415,
  "usage_characters": 4415,
  "output_audio": "/absolute/path/to/voice.wav",
  "raw_timeline": "/absolute/path/to/voice_timeline_raw.json",
  "compact_timeline": "/absolute/path/to/voice_timeline_compact.json",
  "license_status": "aliyun_bailian_standard_tts_system_voice",
  "api_key_source": "DASHSCOPE_API_KEY",
  "retryable": true,
  "task_count": 1,
  "task_audio_dir": "/absolute/path/to/voice_chunks",
  "failed_reason": null
}
```

`voice_timeline_compact.json` must contain paragraph-level records derived from `narration.txt`:

```json
{
  "audio_path": "/absolute/path/to/voice.wav",
  "duration_sec": 123.4,
  "speech_end_sec": 119.9,
  "tail_silence_sec": 3.5,
  "paragraphs": [
    {
      "id": "p001",
      "start_sec": 0.0,
      "end_sec": 12.3,
      "text": "第一段口播文本。",
      "match_status": "matched"
    }
  ]
}
```

## Quality Checklist

- `narration.txt` exists, is non-empty, and contains clean spoken paragraphs.
- `DASHSCOPE_API_KEY` is available before calling TTS.
- `voice.wav`, raw timeline, compact timeline, and `tts_manifest.json` are created.
- Manifests record `api_key_source` only, never the key value.
- Compact timeline paragraph IDs are stable for the run and ordered as `p001`, `p002`, `p003`.
