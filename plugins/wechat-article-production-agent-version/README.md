# WeChat Article Production Agent Version

`wechat-article-production-agent-version` converts a completed Chinese podcast narration into a WeChat Official Account draft.

The only user-facing skill is:

```text
wechat-article-pipeline
```

The workflow is agent-first: the main agent owns user intent, boundaries, configuration, deterministic rendering/upload scripts, and final validation. The article subagent may decide how many images the article actually needs, but must follow the image strategy, retry budget, manifest schema, and failure behavior in the pipeline skill.

## Default Flow

```text
narration.txt
→ .wechat-work/article.json
→ candidate_images from first search results
→ images/ + image_manifest.json
→ prepare_wechat_images.py
→ validate_wechat_article_package.py
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

## Image Strategy

The image workflow prioritizes truthfulness, license transparency, local downloads, and WeChat-hosted final delivery.

- Foreign authoritative open sources remain the highest priority: Wikimedia Commons, NASA, NOAA, Smithsonian Open Access, The Met Open Access, Cleveland Museum of Art Open Access, museums, universities, libraries, archives, research institutions, government open data, and open galleries.
- If preferred sources are inaccessible or unsuitable, the workflow uses limited retries and then falls back to another authoritative source or to domestic official/institutional sources.
- First-round search results are treated as the candidate pool. When high-quality candidates appear, the agent must fetch and download from those candidates instead of continuing to search.
- Mainland China-accessible sources are a fallback and Chinese-topic supplement, not a replacement for reliability priority.
- Open stock galleries such as Unsplash, Pexels, and Pixabay may only support `atmosphere` or `pacing` images.
- AI-generated images are off by default. They are allowed only when the user explicitly asks and must be marked `ai_generated`.
- Reliable images are not mandatory. When none can be found, `image_manifest.json` records a `not_found` placeholder instead of inventing metadata or lowering standards.

## Retry Budget

For each `image_need`:

- turn first-round search results into `candidate_images`;
- process existing high-quality candidates before launching another search;
- try at most 3 high-quality candidate sources;
- try the same URL at most once;
- stop retrying the same domain after consecutive failure;
- fall back or write `license_status: "not_found"` after the budget is exhausted.

The agent must not loop on blocked Wikimedia, NASA, NOAA, museum, archive, or university pages.

## Manifest

`image_manifest.json` records successful images and not-found placeholders. Each item includes role, access status, fallback reason, license status, attempted sources, source URLs, creator, caption, local path, and notes.

Core role values:

```text
evidence
explanation
spatial_orientation
pacing
atmosphere
```

Core status values:

```text
downloaded
timeout
blocked
not_found
skipped
```

## Included Scripts

Run from this plugin root:

```bash
python3 scripts/prepare_wechat_images.py --article-dir /absolute/path/to/narration-wechat
python3 scripts/validate_wechat_article_package.py --article-dir /absolute/path/to/narration-wechat
python3 scripts/render_wechat_html.py --article-dir /absolute/path/to/narration-wechat
python3 scripts/upload_wechat_draft.py --article-dir /absolute/path/to/narration-wechat
```

`prepare_wechat_images.py` rejects HTML/XML error pages, converts SVG to a raster image, and compresses images that exceed conservative WeChat upload limits. `validate_wechat_article_package.py` verifies JSON structure, manifest fields, local image paths, and the 110-character summary safety limit.

`article.html` uses local image paths during production. The upload script uploads body images and cover image to WeChat, then replaces body image URLs in the draft content. Readers should see WeChat-hosted images, not remote source URLs.

## WeChat Credentials

Credentials are read from environment variables first, then from:

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

The workflow creates a draft only. It must never publish, mass-send, delete, or modify existing WeChat assets.
