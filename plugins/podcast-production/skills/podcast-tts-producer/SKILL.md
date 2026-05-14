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
- Do use: `narration.txt`, `narration_meta.json`, and environment variable `DASHSCOPE_API_KEY`.
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
- For the task, send `run-task`, then one combined `continue-task` text containing the whole narration, then `finish-task`.
- Enable `word_timestamp_enabled` in `parameters`.
- Save timestamp data from `result-generated` events.
- Save binary audio exactly as received and append tail silence locally.

## Scripts

Use the low-level bundled script for short text or individual worker chunks:

```text
scripts/cosyvoice_ws_tts.py
```

Typical command:

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 skills/podcast-tts-producer/scripts/cosyvoice_ws_tts.py \
  --narration /absolute/path/to/narration.txt \
  --meta /absolute/path/to/narration_meta.json \
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
  --meta /absolute/path/to/narration_meta.json \
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

The robust script calls `scripts/cosyvoice_ws_tts.py` once per external chunk. Completed chunks are reusable, but this path costs more orchestration and creates more handoff files, so do not use it by default.

## Inputs

Require:

```text
narration.txt
narration_meta.json
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

Never include the actual key.

## Timeline Rules

`voice_timeline_raw.json` stores API-derived sentence/word timing. Preserve:

- `audio_path`
- `model`
- `voice`
- `timeline_source`
- `sentences[].original_text`
- `sentences[].start_ms`
- `sentences[].end_ms`
- `sentences[].words[]`
- `chunks[]` with task IDs, paragraph IDs, local audio paths, duration, offset, sentences, and raw events
- raw events when useful for debugging, excluding credentials

`voice_timeline_compact.json` stores paragraph-level timing for downstream work. Derive paragraph spans from returned word timestamps after applying each chunk's offset.

If a paragraph cannot be matched, mark it with:

```json
{
  "id": "p001",
  "text": "...",
  "match_status": "needs_review",
  "error": "no returned sentence matched this paragraph"
}
```

Do not guess paragraph start/end times when matching fails.

## Voice Stability And Network Resilience

For full episode body narration, prefer direct single-task generation:

- Keep the normal episode body under about 5000 Chinese characters.
- Set `--max-chars-per-task 10000` so one episode becomes one WebSocket task.
- If direct generation fails, write `tts_manifest.json.failed_reason`; do not continue to episode editing.
- Use robust external orchestration only as a fallback for repeated network failures or unusually long text.

For short opening voice or lower-level worker use:

- Keep each WebSocket task within the provider's practical limit; the default pipeline uses one task for ordinary episode bodies.
- Group by paragraph boundaries; do not split a sentence in the middle.
- Within each task, prefer `send_mode=combined` so paragraph boundaries do not become repeated streaming resets. Use `send_mode=paragraph` only for debugging.
- Add 3-5 seconds of tail silence so the ending does not stop abruptly.
- Keep `rate` and `pitch` fixed across chunks.

If the user reports sudden voice changes:

- First retry direct generation once when the network is stable.
- If direct generation repeatedly fails, use `scripts/run_episode_pipeline.py --use-robust-chunking`.
- Try another timestamp-supported system voice only after confirming the text is not too long and the network is stable.
- Avoid Instruct unless using a voice that supports it and the desired style is simple and stable. Instruct can affect emotion but is not a guarantee of timbre consistency.

## Safety And Cost

- Use low concurrency. One WebSocket task at a time is the default.
- Avoid infinite retries. Direct body generation should fail fast enough to leave a useful manifest; robust fallback uses 2 retries per chunk by default.
- Do not test with long full-season text unless the user asks.
- Keep API keys in environment variables only.
- If a key appears in user chat, do not repeat it in outputs.

## Quality Checklist

Before finishing:

- Confirm `voice.wav` exists and is non-empty.
- Confirm `voice_timeline_raw.json`, `voice_timeline_compact.json`, and `tts_manifest.json` are valid JSON.
- Confirm `tts_manifest.json` has no actual API key.
- Confirm `generation_mode` is normally `single_task` for episode body narration.
- Confirm `word_timestamp_enabled` is true.
- Confirm `failed_reason` is null only when audio and timeline were produced.
- Confirm the user has a local path or rendered audio link to listen to the result.
