---
name: wechat-html-publisher
description: Internal component for wechat-article-pipeline. Renders article.html from .wechat-work/article.json plus image_manifest.json, then uploads images and creates a WeChat Official Account draft using environment variables or ~/.codex/wechat.env. Use directly only for HTML rendering or draft upload maintenance.
metadata:
  short-description: 内部组件：微信HTML与草稿上传
---

# WeChat HTML Publisher

## Purpose

Render and upload the article package produced by `wechat-article-pipeline`.

This component reads:

```text
<stem>-wechat/
├── .wechat-work/article.json
├── image_manifest.json
└── images/
```

Final successful output:

```text
<stem>-wechat/
├── article.html
├── image_manifest.json
├── images/
└── wechat_upload_result.json
```

Do not require `article_with_images.md`. Do not leave final `meta.json`.

## Render

```bash
python3 skills/wechat-html-publisher/scripts/render_wechat_html.py \
  --article-dir /path/to/narration-wechat
```

The renderer writes:

- `article.html`
- `.wechat-work/meta.json`

The temporary meta file is for upload only and should be deleted after successful draft creation.

## Upload

```bash
python3 skills/wechat-html-publisher/scripts/upload_wechat_draft.py \
  --article-dir /path/to/narration-wechat
```

The upload script loads configuration from environment variables first, then from:

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

## Rules

- Upload only the `<main>` inner fragment.
- Upload正文 images through `/cgi-bin/media/uploadimg`.
- Upload the cover through `/cgi-bin/material/add_material?type=image`.
- Create a draft through `/cgi-bin/draft/add`.
- Never publish or mass-send.
- Never expose AppSecret.
- Keep title <= 32 Chinese characters.
- Keep author <= 16 Chinese characters.
- Keep digest <= 128 Chinese characters.
- Compress正文 images below 1MB when needed.
- Delete `.wechat-work/` and `.wechat-upload/` after successful upload.
