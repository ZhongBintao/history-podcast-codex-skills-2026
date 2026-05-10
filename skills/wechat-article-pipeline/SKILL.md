---
name: wechat-article-pipeline
description: Primary and recommended external entrypoint for the production Chinese history podcast-to-WeChat article workflow. Use when the user wants to turn a history, civilization, archaeology, culture podcast script, podcast article, blog article, or long-form source text into a structured article package with article.json, downloaded images, image_manifest.json, local WeChat HTML preview, meta.json, and a WeChat Official Account draft. Ask for publishing configuration up front, then run end to end by default without stopping after HTML preview. Prefer this skill over the lower-level wechat-history-article, wechat-image-director, and wechat-html-publisher components.
metadata:
  short-description: 公众号文章总入口：文章到微信草稿
---

# WeChat Article Pipeline

## Overview

This is the only recommended user-facing entrypoint for the WeChat article workflow. The lower-level `wechat-history-article`, `wechat-image-director`, and `wechat-html-publisher` skills are internal production components used by this orchestrator; do not ask the user to invoke them directly during normal operation.

Run the single production workflow:

```text
历史播客脚本/播客文章/博客文章
→ 结构化公众号文章 article.json
→ 图片选择、下载与 image_manifest.json
→ 微信公众号 HTML 预览 article.html + meta.json
→ 自动创建微信公众号草稿
```

Default behavior is to ask for publishing configuration once at the beginning, then run directly through draft creation without stopping after HTML preview. Do not provide staged review/debug modes unless the user explicitly asks for a custom diagnostic run. Draft creation is allowed by default after the up-front configuration check, but publishing or mass-sending is never allowed.

## Up-Front Configuration

Before running the workflow, confirm the publishing configuration in one concise message. Use defaults for anything the user does not specify, except `WECHAT_APPID` and `WECHAT_APPSECRET`, which must come from environment variables or direct user-provided values.

Defaults:

- input type: podcast article or podcast script
- output: create a WeChat draft after HTML generation
- author: `知识的小世界`
- content source URL: empty; do not set `content_source_url`
- comments: enabled
- comment scope: everyone can comment, not fans-only
- HTML preview gate: disabled; do not stop after generating `article.html`
- WeChat action: create draft only, never publish or mass-send

Ask only for missing required sensitive configuration:

```env
WECHAT_APPID=
WECHAT_APPSECRET=
```

Do not ask again for non-sensitive defaults unless the user wants to override them. Never write AppSecret into Markdown, JSON, scripts, logs, or final replies.

## Output Folder

For a podcast script, write a final package next to the input unless the user specifies a destination:

```text
<article-stem>-wechat/
├── article.json
├── article.html
├── meta.json
├── image_manifest.json
└── images/
    ├── cover.<ext>
    ├── 001-<slug>.<ext>
    └── ...
```

Allowed machine intermediate: `article.json`.

Forbidden production outputs:

- `公众号文章_第一版.md`
- `article_with_images.md`
- Markdown as the interface between stages
- three title options
- `封面图候选`

## Stages

Use these skills in order:

1. `$wechat-history-article`: podcast script to structured `article.json`.
2. `$wechat-image-director`: `article.json` to `images/` and `image_manifest.json`.
3. `$wechat-html-publisher`: `article.json` + `image_manifest.json` to `article.html` and `meta.json`.
4. `$wechat-html-publisher` upload mode: create a WeChat draft after HTML generation when `WECHAT_APPID` and `WECHAT_APPSECRET` are available.

## Intake

Identify the current starting point:

- Podcast script, podcast article, blog article, path, or pasted text: start at content restructuring.
- `article.json`: start at image direction or HTML generation if images already exist.
- Folder containing `article.json`, `image_manifest.json`, and `images/`: generate HTML preview.
- Folder containing `article.html` and `meta.json`: ask only whether the user wants draft upload.

If the user provides a relative path, resolve it against the current working directory. Preserve source files.

## Production Workflow

### 1. Content Restructuring

Use `$wechat-history-article`.

Write:

```text
<article-stem>-wechat/article.json
```

Requirements:

- one final title only
- one 100-180 character summary
- sectioned body in `sections`
- no Markdown output
- no internal notes or source commentary

### 2. Image Direction

Use `$wechat-image-director` with `article.json` and the output folder.

Write:

```text
<article-stem>-wechat/image_manifest.json
<article-stem>-wechat/images/
```

Requirements:

- use reliable image sources
- write full source and license metadata in the manifest
- include `placement` for every image
- never write `article_with_images.md`
- never write `封面图候选`

### 3. HTML Preview

Use `$wechat-html-publisher` preview mode.

Run:

```bash
python3 /Users/zhongbintao/.codex/skills/wechat-html-publisher/scripts/render_wechat_html.py \
  --article-dir /path/to/<article-stem>-wechat
```

Write:

```text
article.html
meta.json
```

After generating preview, continue directly to draft creation by default. Do not stop here unless the user explicitly asked for preview-only mode.

Preview files:

- `article.html`
- `meta.json`
- `image_manifest.json`
- `images/`

### 4. Draft Upload

Proceed after HTML generation when the up-front publishing configuration allows draft creation. The default is to create a draft automatically.

Before upload, verify or request:

```env
WECHAT_APPID=
WECHAT_APPSECRET=
```

Use the fixed default author `知识的小世界` unless the user explicitly asks for a different author.

Default upload options:

```env
WECHAT_CONTENT_SOURCE_URL=
WECHAT_NEED_OPEN_COMMENT=1
WECHAT_ONLY_FANS_CAN_COMMENT=0
```

Tell the user:

- AppSecret must not be written into Markdown, JSON, scripts, logs, or final replies.
- If WeChat reports `invalid ip`, `not in whitelist`, or `40164`, add the current server IP to the WeChat public platform IP whitelist.
- Upload creates a draft only. It does not publish or mass-send.
- If `WECHAT_APPID` or `WECHAT_APPSECRET` is missing, stop before upload and explain exactly which environment variable is needed.

## Safety Rules

- Do not publish, mass-send, delete, or modify existing WeChat account assets.
- Do not invent historical facts, image metadata, licenses, URLs, or WeChat API results.
- Do not expose AppSecret.
- If image placeholders or unclear licenses remain, report them before draft upload. If the user allowed automatic draft creation, stop only when the unresolved image issue would make the draft misleading or unusable.
- Final HTML正文 must not display the article title; the title belongs in `meta.json.title` and the WeChat draft title field.
