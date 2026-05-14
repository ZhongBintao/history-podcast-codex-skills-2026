---
name: wechat-article-pipeline
description: Primary external entrypoint for converting a completed Chinese podcast narration file, especially narration.txt, into a WeChat Official Account article draft. Use for history, humanities, culture, science, social science, and other knowledge podcast narrations. The workflow asks for missing WeChat AppID/AppSecret up front, saves them to ~/.codex/wechat.env for reuse, rewrites narration into a WeChat article, selects licensed images, renders article.html, and creates a WeChat draft without producing intermediate Markdown.
metadata:
  short-description: 口播稿到微信公众号草稿
---

# WeChat Article Pipeline

## Purpose

Use this as the only user-facing entrypoint for publishing a completed podcast narration to WeChat.

Default input is a finished `narration.txt` style口播稿. The narration may be history, humanities, culture, science, social science, or another knowledge podcast topic.

## Default Workflow

```text
narration.txt
→ .wechat-work/article.json
→ images/ + image_manifest.json
→ article.html
→ WeChat draft
```

Default output directory is next to the input file:

```text
<stem>-wechat/
├── article.html
├── image_manifest.json
├── images/
└── wechat_upload_result.json
```

Temporary machine files live under `.wechat-work/`. Delete `.wechat-work/` after successful draft upload. Keep it only when a failure needs debugging.

## Up-Front Configuration

At the beginning of the run, check these values:

```env
WECHAT_APPID=
WECHAT_APPSECRET=
WECHAT_AUTHOR=知识的小世界
WECHAT_CONTENT_SOURCE_URL=
WECHAT_NEED_OPEN_COMMENT=1
WECHAT_ONLY_FANS_CAN_COMMENT=0
```

Read existing environment variables first. If `WECHAT_APPID` or `WECHAT_APPSECRET` is missing, ask the user for the missing value before doing the workflow. After the user provides it, write/update `~/.codex/wechat.env` and set file permissions to user-only read/write.

Do not write AppSecret into the repository, generated article files, JSON outputs, logs, or final responses.

Defaults:

- author: `知识的小世界`
- content source URL: empty
- comments: enabled
- fans-only comments: disabled
- action: create draft only

Never publish, mass-send, delete, or modify existing WeChat assets.

## Stages

1. Content restructuring with `wechat-narration-article`.
   - Use it as the narration-to-article component.
   - Write the structured article to `<output>/.wechat-work/article.json`.
   - Do not create Markdown.

2. Image direction with `wechat-image-director`.
   - Read `.wechat-work/article.json`.
   - Write `image_manifest.json` and `images/`.

3. HTML rendering with `wechat-html-publisher`.
   - Render `article.html` from `.wechat-work/article.json` and `image_manifest.json`.
   - Do not write final `meta.json`.

4. Draft upload with `wechat-html-publisher`.
   - Upload正文 images and cover.
   - Create a WeChat draft.
   - Write `wechat_upload_result.json`.
   - Clean `.wechat-work/` and `.wechat-upload/` after success.

## Content Rules

- Preserve the narration's facts, logic, viewpoint, tone, and emotional progression.
- Remove口播-only repetition, filler transitions, excessive rhythm words, and TTS/recording artifacts.
- Do not add facts, numbers, people, concepts, sources, quotes, or causal claims absent from the narration.
- Keep cautious language when the narration is cautious.
- For science topics, preserve the concept chain and explanatory sequence.
- For humanities and social science topics, preserve argument structure and nuance.
- For history and culture topics, preserve chronology, evidence, and uncertainty.

## Forbidden Outputs

- `公众号文章_第一版.md`
- `article_with_images.md`
- final `article.json`
- final `meta.json`
- title option lists
- `封面图候选`

## Completion Report

After success, report only:

- `article.html`
- `image_manifest.json`
- `images/`
- `wechat_upload_result.json`
- draft media id when available
