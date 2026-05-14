# AGENTS.md

## 当前仓库定位

本仓库当前只保留微信公众号文章生产工作流相关 skills。

保留：

- `wechat-article-pipeline`
- `wechat-history-article`
- `wechat-image-director`
- `wechat-html-publisher`

已移除旧 skill：

- `civilization-narrative-director`
- `podcast-script-generator`
- `podcast-voice-script`

这些旧功能后续应被新的综合播客工作流覆盖。

## 当前工作流

`wechat-article-pipeline` 是公众号文章生产总入口，负责将生成好的历史口播稿件转换为可上传微信公众号的文章草稿。

目标流程：

```text
口播稿件
→ 公众号文章结构化内容 article.json
→ 图片选择、下载与授权记录 image_manifest.json
→ 微信公众号 HTML
→ 微信公众号草稿
```

默认行为：

- 不生成中间 Markdown。
- 保留 `article.json` 作为机器结构化中间产物。
- 默认创建微信公众号草稿。
- 只创建草稿，不发布、不群发。

## 后续演进方向

后续要把公众号文章工作流整合进新的播客生产工作流。

理想方向：

- 一个总入口接收历史选题或口播需求。
- 使用 subagent 独立运行两个工作流：
  - 播客工作流：生成可录音的口播稿件。
  - 公众号工作流：基于口播稿件生成公众号文章并上传草稿。
- 两个工作流尽量并行或半并行运行，减少等待时间。
- 最终目标是在生成播客录音内容的同时，自动准备对应微信公众号草稿。

## 修改原则

- 优先维护 `wechat-article-pipeline` 作为对外入口。
- 子 skill 作为内部组件保留，便于后续拆分和并行调用。
- 不恢复旧的 Markdown 分段审核流水线。
- 不恢复旧的独立播客策划/脚本 skill，除非它们被重构进新的总工作流。
