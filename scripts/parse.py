#!/usr/bin/env python3
"""Parse the raw MyGo project list into structured JSON."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "research" / "source-list-tr.md"
OUT = ROOT / "data" / "curated.json"

SECTION_MAP = {
    "Open-source Apps by the Author": "author",
    "✍️ Editors · Notes · Writing": "writing",
    "🤖 AI · Agents · LLM Clients": "ai",
    "🛠 Developer Tools": "dev",
    "🌐 Network · Proxy · Remote": "network",
    "🗂 Storage · Files · Sync": "files",
    "🎵 Media · Players · Download": "media",
    "⚡ Productivity · Menu Bar · Launchers": "productivity",
    "📊 System · Monitoring · Hardware": "system",
    "🎮 Games · Fun": "games",
    "Component Libraries · Templates · Framework Add-ons": "ui",
    "Extra (GitHub aramasından, listede yok)": "extra",
    "Önceki araştırmadan eklenen repolar": "more",
}

# The three "Extra" entries are unambiguous once you read them.
CATEGORY_OVERRIDES = {
    "li-yifei/mygo-straddle-repro": "dev",
    "Simqiqi/simqiqi-music": "media",
    "chemark/xingshu-music": "media",
}

ENTRY_RE = re.compile(r"^-\s+\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s*(.*)$")
LINK_RE = re.compile(r"^-\s+\[([^\]]+)\]\(([^)]+)\)\s*(.*)$")
STAR_RE = re.compile(r"`(\d+)★`")
LICENSE_RE = re.compile(
    r"(?:^|\s)[·—]\s*(MIT|Apache-2\.0|AGPL-3\.0|GPL-3\.0|LGPL-3\.0|BSD-[23]-Clause|MPL-2\.0|Unlicense|ISC)\b"
)
EVIDENCE_RE = re.compile(r"Önceki araştırma:\s*\[([^\]]+)\]\(([^)]+)\)")
EVIDENCE2_RE = re.compile(r"\[(kanıt[^\]]*)\]\(([^)]+)\)")
WEBSITE_RE = re.compile(r"\[Website\]\(([^)]+)\)")
LICENSES = r"(?:MIT|Apache-2\.0|AGPL-3\.0|GPL-3\.0|LGPL-3\.0|BSD-[23]-Clause|MPL-2\.0|Unlicense|ISC)"


def clean(text: str) -> str:
    text = re.sub(r"[·—]\s*Önceki araştırma:.*$", " ", text)
    text = EVIDENCE_RE.sub(" ", text)
    text = EVIDENCE2_RE.sub(" ", text)
    text = WEBSITE_RE.sub(" ", text)
    text = text.replace("❓", " ").replace("🐧", " ")
    for _ in range(4):
        before = text
        text = text.strip()
        text = re.sub(r"^[·—,]\s*", "", text)
        text = re.sub(rf"\s*[·—]\s*{LICENSES}\s*$", "", text)
        text = re.sub(r"\s*[·—]\s*$", "", text)
        text = re.sub(r"\s{2,}", " ", text)
        if text == before:
            break
    return text.strip(" ·—")


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    repos: list[dict] = []
    section = None
    seen: set[str] = set()
    last = None

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("## "):
            section = SECTION_MAP.get(line[3:].strip())
            last = None
            continue
        if line.startswith("### "):
            last = None
            continue
        if not line.startswith("- ") or section is None:
            continue
        if line.startswith("  - "):
            if last is not None:
                note = line.strip()[2:].strip()
                note = re.sub(r"^Ek açıklama \(gönderilen dosyadan\):\s*", "", note)
                if note:
                    last["description"] = (last["description"] + " " + note).strip()
            continue

        m = ENTRY_RE.match(line)
        if m:
            name, url, rest = m.group(1), m.group(2), m.group(3)
            head, _, tail = rest.partition("—")
            stars_m = STAR_RE.search(head)
            lic_m = LICENSE_RE.search(head)
            ev = EVIDENCE_RE.search(rest) or EVIDENCE2_RE.search(rest)
            site = WEBSITE_RE.search(rest)
            entry = {
                "name": name,
                "url": url,
                "description": clean(tail),
                "stars": int(stars_m.group(1)) if stars_m else None,
                "license": lic_m.group(1) if lic_m else None,
                "website": site.group(1) if site else None,
                "evidence": ev.group(2) if ev else None,
                "unverified": "❓" in rest,
                "linux": "🐧" in rest,
                "category": CATEGORY_OVERRIDES.get(name, section),
            }
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            repos.append(entry)
            last = entry
            continue

        m = LINK_RE.match(line)
        if m:
            name, url, rest = m.group(1), m.group(2), m.group(3)
            ev = EVIDENCE2_RE.search(rest)
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            entry = {
                "name": name,
                "url": url,
                "description": "",
                "stars": None,
                "license": None,
                "website": None,
                "evidence": ev.group(2) if ev else None,
                "unverified": False,
                "linux": False,
                "category": "more",
            }
            repos.append(entry)
            last = entry

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repos": repos}, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print("total", len(repos))
    print(Counter(r["category"] for r in repos))
    print("with stars", sum(1 for r in repos if r["stars"]))


if __name__ == "__main__":
    main()
