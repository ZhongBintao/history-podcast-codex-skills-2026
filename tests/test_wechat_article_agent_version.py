import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "wechat-article-production-agent-version" / "scripts"


def run_script(name, *args, check=True):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *map(str, args)],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


SUMMARY = "这是一个用于测试的公众号摘要，保持在安全长度内，能够说明文章主题、结构和阅读价值，同时不会超过微信摘要限制。"


class WechatArticleAgentVersionTests(unittest.TestCase):
    def make_article_dir(self):
        tmp = tempfile.TemporaryDirectory()
        article_dir = Path(tmp.name)
        (article_dir / "article_draft.md").write_text(
            "\n".join(
                [
                    "# 一个最终标题",
                    f"摘要：{SUMMARY}",
                    "## 第一节",
                    "中文引号“测试”、英文引号\"test\"、冒号：和换行都会进入 JSON。",
                    "第二段正文。",
                ]
            )
            + "\n",
            "utf-8",
        )
        (article_dir / "image_candidates.md").write_text(
            "\n".join(
                [
                    "## img-001",
                    "id: img-001",
                    "role: evidence",
                    "placement: before_section:第一节",
                    "visual_need: 一张可靠证据图",
                    "source_page_url: null",
                    "image_url: null",
                    "source_name: null",
                    "creator: null",
                    "license: not_found",
                    "license_status: not_found",
                    "local_path: null",
                    "attempted_sources: Wikimedia Commons, NASA",
                    "notes: 未找到可靠图片。",
                ]
            )
            + "\n",
            "utf-8",
        )
        return tmp, article_dir

    def test_parse_article_draft_writes_article_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            article_dir = Path(tmp)
            (article_dir / "article_draft.md").write_text(
                f"# 标题\n摘要：{SUMMARY}\n## 小标题\n正文包含中文引号“例子”、英文引号\"x\"、冒号：正常。\n",
                "utf-8",
            )
            run_script("parse_article_draft.py", "--article-dir", article_dir)
            data = json.loads((article_dir / ".wechat-work" / "article.json").read_text("utf-8"))
            self.assertEqual(data["title"], "标题")
            self.assertEqual(data["sections"][0]["heading"], "小标题")

    def test_parse_article_draft_rejects_long_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            article_dir = Path(tmp)
            (article_dir / "article_draft.md").write_text(
                "# 标题\n摘要：" + ("长" * 111) + "\n## 小标题\n正文。\n",
                "utf-8",
            )
            result = run_script("parse_article_draft.py", "--article-dir", article_dir, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("summary exceeds", result.stderr)

    def test_parse_image_candidates_writes_not_found_placeholder(self):
        tmp, article_dir = self.make_article_dir()
        with tmp:
            run_script("parse_image_candidates.py", "--article-dir", article_dir)
            manifest = json.loads((article_dir / "image_manifest.json").read_text("utf-8"))
            self.assertEqual(manifest[0]["license_status"], "not_found")
            self.assertIsNone(manifest[0]["local_path"])
            self.assertEqual(manifest[0]["fallback_reason"], "no_reliable_candidate")

    def test_parse_image_candidates_rejects_stock_evidence(self):
        tmp, article_dir = self.make_article_dir()
        with tmp:
            text = (article_dir / "image_candidates.md").read_text("utf-8")
            text = text.replace("license: not_found", "license: Unsplash License")
            text = text.replace("license_status: not_found", "license_status: stock_license")
            text = text.replace("local_path: null", "local_path: images/example.jpg")
            (article_dir / "images").mkdir()
            (article_dir / "images" / "example.jpg").write_bytes(b"\xff\xd8\xff\xdb")
            (article_dir / "image_candidates.md").write_text(text, "utf-8")
            result = run_script("parse_image_candidates.py", "--article-dir", article_dir, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("evidence image cannot use stock_license", result.stderr)

    def test_package_runner_and_preflight_guard(self):
        tmp, article_dir = self.make_article_dir()
        with tmp:
            run_script("run_wechat_article_package.py", "--article-dir", article_dir)
            self.assertTrue((article_dir / "article.html").exists())
            self.assertTrue((article_dir / ".wechat-work" / "preflight.json").exists())

            run_script("render_wechat_html.py", "--article-dir", article_dir)
            with (article_dir / "article_draft.md").open("a", encoding="utf-8") as handle:
                handle.write("\n追加修改。\n")
            result = run_script("render_wechat_html.py", "--article-dir", article_dir, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("changed after preflight", result.stderr + result.stdout)

    def test_validate_rejects_remote_html_image(self):
        tmp, article_dir = self.make_article_dir()
        with tmp:
            run_script("run_wechat_article_package.py", "--article-dir", article_dir)
            (article_dir / "article.html").write_text('<img src="https://example.com/a.jpg">\n', "utf-8")
            result = run_script(
                "validate_wechat_article_package.py",
                "--article-dir",
                article_dir,
                "--require-html",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote image URL", result.stderr)


if __name__ == "__main__":
    unittest.main()
