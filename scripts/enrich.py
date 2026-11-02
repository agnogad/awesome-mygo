#!/usr/bin/env python3
"""Fetch live metadata for every repo via the GitHub CLI and cache it."""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "repos.json"
CACHE = ROOT / "data" / "github.json"


def fetch(slug: str) -> tuple[str, dict]:
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{slug}", "--jq",
             "{name:.full_name,description:.description,stars:.stargazers_count,"
             "license:.license.spdx_id,homepage:.homepage,topics:.topics,"
             "archived:.archived,pushed:.pushed_at,language:.language,fork:.fork}"],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode == 0:
            return slug, json.loads(out.stdout)
        return slug, {"error": out.stderr.strip()[:200]}
    except Exception as exc:  # noqa: BLE001
        return slug, {"error": str(exc)[:200]}


def main() -> None:
    repos = json.loads(DATA.read_text(encoding="utf-8"))["repos"]
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    todo = [r["name"] for r in repos if r["name"] not in cache or "error" in cache.get(r["name"], {})]
    print(f"fetching {len(todo)} / {len(repos)}")
    with ThreadPoolExecutor(max_workers=8) as pool:
        for slug, meta in pool.map(fetch, todo):
            cache[slug] = meta
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    errs = [k for k, v in cache.items() if "error" in v]
    print("errors", len(errs), errs[:10])


if __name__ == "__main__":
    main()
