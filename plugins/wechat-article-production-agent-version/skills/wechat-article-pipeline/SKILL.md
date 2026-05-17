---
name: wechat-article-pipeline
description: Primary and only external entrypoint for converting a completed Chinese podcast narration file, especially narration.txt, into a WeChat Official Account article draft. Use for history, humanities, culture, science, social science, and other knowledge narrations. This agent-version workflow writes article.json, applies a bounded transparent image sourcing strategy, renders article.html with local images, and creates a WeChat draft when credentials are available.
metadata:
  short-description: 口播稿到公众号草稿，含新版有限重试配图策略
---

# WeChat Article Pipeline

## Purpose

Use this as the only user-facing entrypoint for publishing a completed podcast narration to WeChat.

Default input is a finished `narration.txt` style口播稿. The narration may be history, humanities, culture, science, social science, or another knowledge podcast topic.

This agent-version skill keeps one public entrypoint. The main agent owns user intent, credential checks, boundaries, deterministic scripts, validation, and reporting. The article subagent may make article and image decisions within the rules below, but must not invent facts, image metadata, licenses, or source URLs.

## Default Workflow

```text
narration.txt
→ .wechat-work/article.json
→ image_needs planning
→ candidate_images from first search results
→ images/ + image_manifest.json
→ prepare_wechat_images.py
→ validate_wechat_article_package.py
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

Read existing environment variables first. If `WECHAT_APPID` or `WECHAT_APPSECRET` is missing, ask the user for the missing value before attempting draft upload. If the user provides it, write/update `~/.codex/wechat.env` and set file permissions to user-only read/write.

Do not write AppSecret into the repository, generated article files, JSON outputs, logs, task packets, or final responses.

Defaults:

- author: `知识的小世界`
- content source URL: empty
- comments: enabled
- fans-only comments: disabled
- action: create draft only

Never publish, mass-send, delete, or modify existing WeChat assets.

## Article Output

Write this JSON object to `<output>/.wechat-work/article.json`:

```json
{
  "title": "一个最终标题",
  "summary": "100-110 个中文字符以内的摘要/导语。",
  "sections": [
    {
      "heading": "小标题",
      "paragraphs": ["段落一", "段落二"]
    }
  ]
}
```

Rules:

- Generate exactly one title.
- Keep `summary` within 100-110 Chinese characters. Do not approach the WeChat API limit.
- Do not produce Markdown, title option lists, rewrite notes, source lists, or internal commentary.
- Do not hand-write large JSON files as raw text. Write `article.json` with a JSON serializer, for example `json.dumps(data, ensure_ascii=False, indent=2)`.
- Preserve the narration's facts, logic, viewpoint, tone, emotional progression, and necessary personal expression.
- Remove口播-only repetition, filler transitions, recording/TTS artifacts, and excessive rhythm words.
- Keep about 70%-85% of the source information density unless the user asks otherwise.
- Do not add facts, numbers, people, concepts, sources, quotes, scenes, psychology, or causal claims absent from the narration.
- Preserve uncertainty markers such as `可能`, `大概`, `估计`, `有些学者`, `据称`, and `存在争议`.

## Image Planning First

After `.wechat-work/article.json` exists, decide where images are genuinely useful. Do not force every section to have a picture.

Create `image_needs` before searching. Each item must include:

```json
{
  "role": "evidence",
  "placement": "before_section:...",
  "visual_need": "需要什么画面或图表",
  "why_this_image_matters": "它如何帮助理解文章",
  "preferred_source_types": ["Wikimedia Commons", "museum open access"],
  "fallback_allowed": ["foreign_authoritative_open", "domestic_official_institutional"]
}
```

Image roles:

- `evidence`: evidence image, artifact, archive image, real place, scientific image, official chart. Must come from reliable sources. Do not replace with open stock galleries or AI images.
- `explanation`: mechanism, structure, map, concept relationship, process, or chart. Prefer official institutions, open data, research institutions, governments, or universities.
- `spatial_orientation`: geography, location, scene, or site orientation. Use maps, satellite imagery, institutional photos, or official place imagery when reliable.
- `pacing`: reading rhythm. May use reliable related images or open stock galleries when clearly non-evidentiary.
- `atmosphere`: abstract cover or non-evidence mood image. May use open stock galleries. The manifest must say it is not evidence.

## Image Source Strategy

Use sources in this priority order.

1. Foreign authoritative open sources, highest priority:
   - Wikimedia Commons
   - NASA
   - NOAA
   - Smithsonian Open Access
   - The Met Open Access
   - Cleveland Museum of Art Open Access
   - museums, universities, libraries, archives, research institutions, government open data, or open galleries
   - Best for evidence images, artifacts, scientific imagery, maps, historical photos, institutional charts, and public-domain or open-license material.

2. Domestic official or institutional sources, fallback and Chinese-topic supplement:
   - Mainland China government departments
   - museums, culture and tourism bureaus, archives, universities, research institutes
   - official press releases, public report PDFs, local government portals
   - People's Daily Online, Xinhua, CCTV, China.org.cn, and comparable authoritative media
   - These may be reliable, but copyright status is often unclear. Label that honestly.

3. Open stock galleries, atmosphere only:
   - Unsplash, Pexels, Pixabay, and similar services
   - Use only for atmosphere, pacing, abstract cover, or non-factual scenes.
   - Never present these images as a specific historical photo, person, scientific evidence, place evidence, artifact, or archive material.

4. AI-generated images:
   - Do not use by default.
   - Use only when the user explicitly requests AI-generated images.
   - Mark as `ai_generated`.
   - Never disguise AI images as real photos, artifacts, archives, scenes, scientific evidence, or official diagrams.

China-mainland accessibility is a fallback dimension, not a replacement for reliability priority. The production test is whether the agent can successfully download the chosen image to local `images/`.

## Search And Retry Budget

For every `image_need`:

- Treat first-round WebSearch results as the candidate pool. If high-quality sources appear in the first round, immediately process them with WebFetch instead of launching more searches.
- Write `candidate_images` before downloading. Each candidate should track `candidate_url`, `source_type`, `domain`, `expected_role`, and why it may satisfy the image need.
- Process candidates in priority order: WebFetch candidate page, extract reliable image URL and license metadata, download to `images/`, run `prepare_wechat_images.py`, then update `image_manifest.json`.
- Do not run another WebSearch while there are unprocessed high-quality candidates for the same image need.
- Try at most 3 high-quality candidate sources.
- Try the same URL at most 1 time.
- If the same domain fails consecutively, stop opening more pages from that domain for this need.
- If the preferred source times out, is blocked, has unclear rights, or has no reliable candidate, move to the next source tier.
- If the need still fails, write a `not_found` placeholder in `image_manifest.json`.
- Do not loop in the conversation with unlimited "try again" attempts.
- If Wikimedia, NASA, NOAA, museums, archives, universities, or other preferred sources are inaccessible in the current agent environment, do not lower truthfulness standards to fill the slot.

Finding no reliable image is acceptable. Faking a source, forcing a low-quality substitute, or repeatedly retrying blocked sources is a workflow failure.

## Fallback Rules

When the highest-priority source fails or lacks a suitable image:

1. Try another foreign authoritative open source.
2. Try a domestic official or institutional source.
3. If the role is `atmosphere` or `pacing`, open stock galleries are allowed.
4. If no reliable image remains, write `license_status: "not_found"`.
5. Never use unclear reposts, social media copies, Pinterest, random blogs, watermarked images, movie/TV screenshots, stock previews, or untraceable files as final images.

## Manifest

Write `image_manifest.json` as a JSON array. Include successful images and not-found placeholders.

Every item must include:

```json
{
  "id": "img-001",
  "type": "cover",
  "role": "evidence",
  "local_path": "images/cover.jpg",
  "caption": "图片说明",
  "placement": "cover",
  "source_page_url": "https://...",
  "image_url": "https://...",
  "source_name": "Wikimedia Commons",
  "creator": "Unknown",
  "license": "CC BY-SA 4.0",
  "license_status": "open_license",
  "access_status": "downloaded",
  "fallback_reason": null,
  "attempted_sources": ["Wikimedia Commons"],
  "notes": "用于说明..."
}
```

Allowed `role` values:

- `evidence`
- `explanation`
- `spatial_orientation`
- `pacing`
- `atmosphere`

Allowed `access_status` values:

- `downloaded`
- `timeout`
- `blocked`
- `not_found`
- `skipped`

Allowed `fallback_reason` values:

- `preferred_source_timeout`
- `preferred_source_blocked`
- `no_reliable_candidate`
- `license_unclear`
- `not_needed`
- `null`

Allowed `license_status` values:

- `open_license`
- `public_domain`
- `official_source_rights_unclear`
- `stock_license`
- `ai_generated`
- `not_found`

For not-found items, keep the placeholder:

```json
{
  "id": "img-003",
  "type": "body",
  "role": "evidence",
  "local_path": null,
  "caption": "未找到可靠图片",
  "placement": "before_section:...",
  "source_page_url": null,
  "image_url": null,
  "source_name": null,
  "creator": null,
  "license": null,
  "license_status": "not_found",
  "access_status": "not_found",
  "fallback_reason": "preferred_source_timeout",
  "attempted_sources": ["Wikimedia Commons", "NASA Images"],
  "notes": "可人工搜索关键词：..."
}
```

Use production wording only. Never write `封面图候选`.

## Local Image And WeChat Upload Rules

- Production images must be downloaded to local `images/`.
- After downloading images and writing `image_manifest.json`, run `prepare_wechat_images.py` before rendering HTML.
- `prepare_wechat_images.py` owns WeChat image compatibility: reject HTML/XML error pages, convert SVG to raster images, compress oversized body images and covers, and update `local_path` when a prepared copy is created.
- The AI owns source reliability and license transparency; the script owns format, size, and local image compatibility.
- `article.html` uses local image paths.
- Source URLs in the manifest exist only for source tracing and license transparency.
- Draft upload must upload body images to WeChat and replace body image URLs with WeChat-hosted URLs.
- Upload the cover through WeChat permanent material image upload.
- The final reader experience must not depend on remote source image URLs being accessible.
- If `local_path` is null, do not reference a remote image URL in `article.html`.

## Rendering

Before rendering, validate the package:

```bash
python3 scripts/validate_wechat_article_package.py \
  --article-dir /path/to/narration-wechat
```

Run from this plugin root:

```bash
python3 scripts/render_wechat_html.py \
  --article-dir /path/to/narration-wechat
```

The renderer writes:

- `article.html`
- `.wechat-work/meta.json`

The temporary meta file is for upload only and should be deleted after successful draft creation.

## Draft Upload

Prepare images before rendering and uploading:

```bash
python3 scripts/prepare_wechat_images.py \
  --article-dir /path/to/narration-wechat
```

Run from this plugin root:

```bash
python3 scripts/upload_wechat_draft.py \
  --article-dir /path/to/narration-wechat
```

The upload script loads configuration from environment variables first, then from `~/.codex/wechat.env`.

Rules:

- Upload only the `<main>` inner fragment.
- Upload正文 images through `/cgi-bin/media/uploadimg`.
- Upload the cover through `/cgi-bin/material/add_material?type=image`.
- Create a draft through `/cgi-bin/draft/add`.
- Never publish or mass-send.
- Never expose AppSecret.
- Keep title <= 32 Chinese characters.
- Keep author <= 16 Chinese characters.
- Keep digest/summary <= 110 Chinese characters as a conservative local safety limit.
- Do not rely on upload-time compression for normal production. Run `prepare_wechat_images.py` first.
- Upload refuses remote image URLs, missing local images, oversized covers, and packages that fail `validate_wechat_article_package.py`.
- Delete `.wechat-work/` and `.wechat-upload/` after successful upload.

## Forbidden Outputs

- `公众号文章_第一版.md`
- `article_with_images.md`
- final `article.json`
- final `meta.json`
- title option lists
- `封面图候选`
- raw hand-written large JSON for `article.json` or `image_manifest.json`

## Forbidden Image Behaviors

- Forging URLs, creators, institutions, license names, or source metadata.
- Using random blogs, Pinterest, social media reposts, watermarked images, movie/TV screenshots, stock previews, or untraceable files as final images.
- Using atmosphere images as evidence images.
- Using AI-generated images as real photos, artifacts, archives, official diagrams, site images, or scientific evidence.
- Infinite retrying of the same failed source, URL, or domain.
- Lowering truthfulness standards just to fill an image slot.
- Marking unclear copyright as open license.
- Referencing an unstable remote image URL in `article.html` when no local image exists.

## Validation Checklist

Before final reporting, verify:

- `wechat-article-pipeline` is the only user-facing skill in this plugin.
- `.wechat-work/article.json` exists during production and contains one title, one summary, and sections.
- `image_manifest.json` includes `role`, `access_status`, `fallback_reason`, `license_status`, and `attempted_sources`.
- `article.json` and `image_manifest.json` were written through a JSON serializer, not manually composed as raw JSON text.
- `prepare_wechat_images.py` has run after image download and before HTML rendering.
- `validate_wechat_article_package.py` passes before rendering/uploading.
- Every downloaded image has a local file under `images/`.
- Not-found image needs are represented with `license_status: "not_found"` instead of fake metadata.
- Evidence images never use open stock galleries or AI-generated images as substitutes.
- `article.html` does not reference remote URLs for missing local images.
- `plugin.json` and marketplace JSON remain valid JSON.

## Completion Report

After success, report only:

- `article.html`
- `image_manifest.json`
- `images/`
- `wechat_upload_result.json`
- draft media id when available
