#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "skills/writer_registry.json"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def domain_matches(domain, writer):
    wanted = domain.strip().lower()
    if not wanted:
        return False
    if wanted in str(writer.get("skill", "")).lower():
        return True
    return wanted in [str(item).lower() for item in writer.get("domains", [])]


def resolve_writer(domain, registry):
    writers = registry.get("writers") or {}
    default = registry.get("default_writer") or {}
    matched_key = None
    matched = None
    for key, writer in writers.items():
        if key.lower() == domain.lower() or domain_matches(domain, writer):
            matched_key = key
            matched = writer
            break

    if matched and matched.get("available") is True:
        return {
            "content_domain": domain,
            "writer_registry_key": matched_key,
            "recommended_writer_skill": matched["skill"],
            "writer_selection_source": "writer_registry",
            "writer_fallback_reason": None,
            "required_inputs": matched.get("required_inputs", ["episode_brief.json"]),
            "default_outputs": matched.get("default_outputs", ["script_full.md"]),
            "optional_outputs": matched.get("optional_outputs", ["fact_check.md"]),
            "fact_check_policy": matched.get("fact_check_policy"),
        }

    fallback_skill = None
    reason = None
    if matched:
        fallback_skill = matched.get("fallback_skill") or default.get("skill")
        reason = f"writer {matched.get('skill')} for domain {domain!r} is registered but not available"
    else:
        fallback_skill = default.get("skill")
        reason = f"no writer registered for domain {domain!r}"
    if default.get("fallback_reason"):
        reason = f"{reason}; {default['fallback_reason']}"

    return {
        "content_domain": domain,
        "writer_registry_key": matched_key,
        "recommended_writer_skill": fallback_skill,
        "writer_selection_source": "writer_registry",
        "writer_fallback_reason": reason,
        "required_inputs": ["episode_brief.json"],
        "default_outputs": ["script_full.md"],
        "optional_outputs": ["fact_check.md"],
        "fact_check_policy": "follow the selected writer skill and episode brief",
    }


def validate_registry(registry):
    errors = []
    if registry.get("version") != 1:
        errors.append("registry version must be 1")
    default_skill = (registry.get("default_writer") or {}).get("skill")
    if not default_skill:
        errors.append("default_writer.skill is required")
    writers = registry.get("writers")
    if not isinstance(writers, dict) or not writers:
        errors.append("writers must be a non-empty object")
        return errors
    for key, writer in writers.items():
        if not writer.get("skill"):
            errors.append(f"{key}: skill is required")
        if not isinstance(writer.get("available"), bool):
            errors.append(f"{key}: available must be boolean")
        if not writer.get("domains"):
            errors.append(f"{key}: domains must be non-empty")
        if writer.get("required_inputs") != ["episode_brief.json"]:
            errors.append(f"{key}: required_inputs must be ['episode_brief.json']")
        if "script_full.md" not in (writer.get("default_outputs") or []):
            errors.append(f"{key}: default_outputs must include script_full.md")
        if writer.get("available") is False and not (writer.get("fallback_skill") or default_skill):
            errors.append(f"{key}: unavailable writer needs fallback_skill or default_writer.skill")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Resolve podcast writer skill from writer registry.")
    parser.add_argument("--domain", help="Content domain to resolve, such as history, science, or humanities.")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    registry = load_json(args.registry)
    errors = validate_registry(registry)
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    if args.validate and not args.domain:
        print("PASS writer registry is valid")
        return 0
    if not args.domain:
        parser.error("provide --domain or --validate")
    print(json.dumps(resolve_writer(args.domain, registry), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
