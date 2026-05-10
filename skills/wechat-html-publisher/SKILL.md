---
name: wechat-html-publisher
description: Internal component for the wechat-article-pipeline skill. Generates WeChat-compatible HTML and meta.json from article.json, image_manifest.json, and local images, then can upload the generated preview as a WeChat Official Account draft when the orchestrator has already confirmed publishing configuration. Prefer the public wechat-article-pipeline entrypoint for normal user requests; use this directly only when explicitly asked to work on HTML rendering or draft upload.
metadata:
  short-description: 内部组件：微信HTML预览与草稿上传
---

# WeChat HTML Publisher

## Purpose

This is a lower-level production component. For normal podcast-to-WeChat work, use `wechat-article-pipeline` as the external entrypoint and let it call this component.

Render a structured article package into local WeChat-compatible preview files:

```text
<article-stem>-wechat/
├── article.json
├── article.html
├── meta.json
├── image_manifest.json
└── images/
```

This skill no longer reads `article_with_images.md` and does not depend on Markdown heading parsing.

## Modes

1. **HTML preview**: generate local `article.html` and `meta.json`.
2. **WeChat draft upload**: upload images and create a draft when the orchestrator has already confirmed publishing configuration.

Draft upload creates real account-side draft/media assets, but does not publish or mass-send.

## Preview Rules

- Read the title from `article.json.title`.
- Read the summary from `article.json.summary`.
- Read body content from `article.json.sections`.
- Read cover and inline image placement from `image_manifest.json`.
- Do not display the article title in the正文 HTML.
- Do not display the public-account brand name in the正文 HTML.
- Put the cover image and caption at the top when present.
- Render the summary in a modern white box.
- Render section headings with a left red-brown accent line.
- Render images at manifest placements, 100% width, with restrained centered captions.
- Generate a plain white `图片来源` section from `image_manifest.json`.
- Remove unnecessary blank lines.
- Clean any accidental `封面图候选：` or `封面图候选` wording while rendering.

## Scripts

Generate preview HTML:

```bash
python3 /Users/zhongbintao/.codex/skills/wechat-html-publisher/scripts/render_wechat_html.py \
  --article-dir /path/to/article-wechat-folder
```

The directory must contain `article.json` and `image_manifest.json`. You may also pass an explicit article path:

```bash
python3 /Users/zhongbintao/.codex/skills/wechat-html-publisher/scripts/render_wechat_html.py \
  --article-json /path/to/article.json \
  --article-dir /path/to/article-wechat-folder
```

Create a WeChat draft after the orchestrator has confirmed publishing configuration:

```bash
WECHAT_APPID='...' WECHAT_APPSECRET='...' \
python3 /Users/zhongbintao/.codex/skills/wechat-html-publisher/scripts/upload_wechat_draft.py \
  --article-dir /path/to/article-wechat-folder \
  --need-open-comment 1 \
  --only-fans-can-comment 0
```

The upload script defaults to author `知识的小世界`, enabled comments, no fans-only comment restriction, and empty `content_source_url`. Pass `--author` or `--content-source-url` only when the user explicitly requests different values.

## Preview Workflow

1. Locate the output folder containing `article.json`, `image_manifest.json`, and `images/`.
2. Run `scripts/render_wechat_html.py`.
3. Optionally preview `article.html` locally when the user asked for preview-only mode.
4. Report:
   - `article.html`
   - `meta.json`
   - `image_manifest.json`
   - `images/`

## Draft Upload Requirements

Proceed when the orchestrator has already confirmed upload configuration. In normal pipeline use, this happens at the beginning of the workflow, so do not ask again after HTML generation.

Before uploading, verify or request:

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

Warn the user:

- AppSecret must not be written to Markdown, JSON, scripts, logs, or final replies.
- If WeChat reports `invalid ip`, `not in whitelist`, or `40164`, the current server IP must be added to the WeChat public platform IP whitelist.
- This creates a draft only. It does not publish or mass-send.

## WeChat Compatibility

The upload script must:

1. Extract only the `<main>` inner article fragment.
2. Upload正文 images through `/cgi-bin/media/uploadimg`.
3. Replace local image paths with WeChat image URLs.
4. Upload the cover through `/cgi-bin/material/add_material?type=image`.
5. Use the returned `thumb_media_id`.
6. Create the draft through `/cgi-bin/draft/add`.

Keep limits in mind:

- title <= 32 Chinese characters
- author <= 16 Chinese characters
- digest <= 128 Chinese characters
- content should stay below 20,000 characters when possible
-正文 images should be jpg/png and under 1MB after compression

## Do Not

- Do not publish or mass-send.
- Do not create a draft if `WECHAT_APPID` or `WECHAT_APPSECRET` is unavailable.
- Do not upload repeatedly unless the user asks for another version.
- Do not expose AppSecret.
- Do not use random external images at this stage.
- Do not require or read `article_with_images.md`.
