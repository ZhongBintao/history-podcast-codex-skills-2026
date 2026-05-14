# History Podcast Codex Skills 交接文档

更新时间：2026-05-14

## 1. 仓库定位

本仓库保存历史/知识类播客生产相关 Codex skills。当前稳定目标是两条工作流并存：

- 播客声音生产工作流：从系列策划到 voice-only `episode.mp3`。
- 微信公众号文章工作流：将口播稿件转成可上传微信公众号的文章草稿。

仓库不再保留旧的独立播客策划、播客脚本生成、口播稿生成 skills；这些能力已经被新的播客生产工作流覆盖。

## 2. 当前保留 Skills

### 播客声音生产

唯一用户入口：

```text
skills/podcast-series-showrunner/
```

内部模块：

```text
skills/podcast-series-opening-voice-producer/
skills/podcast-episode-director/
skills/history-script-writer/
skills/podcast-narration-adapter/
skills/podcast-tts-producer/
skills/podcast-episode-editor/
```

稳定产物：

```text
series_plan.json
series_opening_voice.md
series_opening_voice.json
opening_voice.wav
opening_voice_tts_manifest.json
production_state.json
episodes/epXX-<slug>/episode_brief.json
episodes/epXX-<slug>/script_full.md
episodes/epXX-<slug>/fact_check.md
episodes/epXX-<slug>/script_meta.json
episodes/epXX-<slug>/narration.txt
episodes/epXX-<slug>/narration_meta.json
episodes/epXX-<slug>/voice.wav
episodes/epXX-<slug>/voice_timeline_raw.json
episodes/epXX-<slug>/voice_timeline_compact.json
episodes/epXX-<slug>/tts_manifest.json
episodes/epXX-<slug>/episode.mp3
episodes/epXX-<slug>/production_manifest.json
```

边界：

- 只生产完整口播版音频。
- 不生成、选择、下载、入库或混合音乐和音效。
- `narration.txt` 必须保持干净，只给 TTS 使用。
- API Key 只能来自环境变量，例如 `DASHSCOPE_API_KEY`，不得写入任何文件。

### 微信公众号文章生产

总入口：

```text
skills/wechat-article-pipeline/
```

内部模块：

```text
skills/wechat-history-article/
skills/wechat-image-director/
skills/wechat-html-publisher/
```

稳定产物：

```text
article.json
image_manifest.json
images/
article.html
meta.json
微信公众号草稿
```

边界：

- 默认创建微信公众号草稿。
- 不发布、不群发、不删除账号资产。
- 不把 WeChat AppSecret 写入 Markdown、JSON、脚本、日志或最终回复。

## 3. 确定性工具

```text
tools/robust_episode_tts.py
tools/run_episode_pipeline.py
tools/validate_production.py
```

`tools/run_episode_pipeline.py` 只负责播客音频后半段，不调用 LLM，不生成 brief、脚本或口播适配文本。

```bash
DASHSCOPE_API_KEY="$DASHSCOPE_API_KEY" python3 tools/run_episode_pipeline.py \
  --series-dir /absolute/path/to/series \
  --episode-dir /absolute/path/to/series/episodes/ep01-title
```

`tools/validate_production.py` 用于上传、交接或续跑前做机器校验。

```bash
python3 tools/validate_production.py --series-dir /absolute/path/to/series
python3 tools/validate_production.py --episode-dir /absolute/path/to/series/episodes/ep01-title --strict
```

## 4. 后续演进方向

下一阶段要把微信公众号文章工作流整合进播客生产工作流，但保持两个工作流可独立运行。

目标形态：

```text
用户提出历史/知识类播客选题
→ podcast-series-showrunner 统一澄清需求和确定系列方案
→ 播客工作流生成 script_full.md、narration.txt、episode.mp3
→ 公众号文章工作流读取同一集脚本或口播稿，生成 article.json、HTML 和微信公众号草稿
```

推荐并行策略：

- 默认仍由 `podcast-series-showrunner` 作为总入口。
- 当单集 `script_full.md` 或 `narration.txt` 稳定后，可以启动一个独立 subagent 运行 `wechat-article-pipeline`。
- 主线程继续执行 TTS 和 `episode.mp3` 生产。
- WeChat subagent 独立生成文章包和公众号草稿，不阻塞音频 TTS。
- 两个工作流通过明确文件路径交接，不共享可写中间文件。
- 最终在 `production_state.json` 或后续扩展的 manifest 中记录对应文章目录和草稿状态。

未来整合时应注意：

- 公众号文章应基于已确认脚本或口播稿，不重新发明事实和叙事主线。
- 播客音频失败不应自动取消文章草稿生成；文章 workflow 可以独立完成。
- 公众号上传失败不应影响已经完成的 `episode.mp3`。
- 两个 workflow 都必须避免泄露 API key、AppSecret 或上传凭证。
- 发布和群发仍然需要人类明确授权；自动流程只创建草稿。

## 5. GitHub 维护规则

仓库应包含：

- 稳定播客 skills
- 稳定 WeChat skills
- `tools/`
- `AGENTS.md`
- `README.md`
- `.gitignore`

仓库不应包含：

- `.venv/`
- `.DS_Store`
- `__pycache__/`
- 本地测试系列产物
- 生成音频
- API key、AppSecret 或含密钥日志

提交前至少运行：

```bash
python3 -m py_compile tools/*.py \
  skills/podcast-tts-producer/scripts/*.py \
  skills/podcast-episode-editor/scripts/*.py \
  skills/wechat-html-publisher/scripts/*.py
```

如有测试系列产物，运行：

```bash
python3 tools/validate_production.py --series-dir /absolute/path/to/series
```
