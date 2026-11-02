#!/usr/bin/env python3
"""Merge curated entries with live GitHub metadata into the final dataset."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "data" / "curated.json"
REPOS = ROOT / "data" / "repos.json"
GH = ROOT / "data" / "github.json"
OVERRIDES = ROOT / "data" / "overrides.json"
SITE = ROOT / "site" / "data.json"

CATEGORIES = [
    ("author", "Apps by the Author", "Open-source apps built by the creator of MyGo."),
    ("ai", "AI, Agents & LLM Clients", "Coding agents, chat clients, voice input, token trackers and agent workbenches."),
    ("dev", "Developer Tools", "Git clients, terminals, API clients, database GUIs, Kubernetes and infra tooling."),
    ("writing", "Editors, Notes & Writing", "Code editors, Markdown notebooks, email clients and writing apps."),
    ("media", "Media, Players & Download", "Music and video players, downloaders and media library front ends."),
    ("productivity", "Productivity, Menu Bar & Launchers", "Launchers, timers, scratchpads and the small utilities that live in your menu bar."),
    ("system", "System, Monitoring & Hardware", "System monitors, display and hardware control, desktop-shell experiments."),
    ("files", "Storage, Files & Sync", "Object storage, backup, clipboard, file managers and disk tools."),
    ("network", "Network, Proxy & Remote", "Proxy clients, VPNs, campus-network helpers and remote access."),
    ("games", "Games & Fun", "Games, game tooling, calculators and playful experiments."),
    ("ui", "UI Kits, Templates & Add-ons", "Component libraries, app shells, icon sets and starter templates."),
    ("more", "More Projects Using MyGo", "Additional repositories with a verified MyGo dependency."),
]
ORDER = {cid: i for i, (cid, _, _) in enumerate(CATEGORIES)}

# Projects that arrived in the "more" bucket from later research; each one has a
# clear home once you read its description.
CATEGORY_FIX = {
    "egoist/lorca": "ai",
    "digiogithub/pando": "ai",
    "VaalaCat/openvaala": "ai",
    "zzstar101/mytoken": "ai",
    "cheese-zj/openconnector": "ai",
    "ca-x/lark": "media",
    "welllog/otool": "dev",
    "jhzhang09/gocompare": "dev",
    "hoanglong2311/mcpgw": "dev",
    "li-yifei/lom-dx2metal": "dev",
    "Seevil/webtools": "dev",
    "logseq/lui": "ui",
    "yldm-tech/nodra": "ui",
    "firede/limu": "ui",
    "VaalaCat/mygo-kit": "ui",
    "josexy/nuxt-ui-go": "ui",
    "echoVic/little-reef": "productivity",
    "Viking602/YoloMCL": "games",
    "rksvc/sav": "games",
    "Qsnh/lanscout": "network",
    "bitoolkit/biternet-go": "network",
    "qmaru/wgm": "network",
    "reixie/keeps": "files",
    "L92-Labs/myclip": "files",
    "tbdsux/keydepot": "files",
}


def plain(text: str) -> str:
    """Strip inline Markdown and normalise sentence endings."""
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"\s{2,}", " ", text).strip()
    text = text.rstrip(" ·—,")
    if text and text[-1] not in ".!?…":
        text += "."
    return text


def main() -> None:
    curated = json.loads(CURATED.read_text(encoding="utf-8"))["repos"]
    gh = json.loads(GH.read_text(encoding="utf-8"))
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    config = json.loads((ROOT / "data" / "config.json").read_text(encoding="utf-8"))
    out = []

    for repo in curated:
        meta = gh.get(repo["name"], {})
        ok = "error" not in meta
        desc = overrides.get(repo["name"]) or repo["description"].strip()
        api_desc = (meta.get("description") or "").strip() if ok else ""
        if not desc:
            desc = api_desc
        desc = plain(desc)
        lic = meta.get("license") if ok else None
        if lic in (None, "NOASSERTION", ""):
            lic = repo["license"]
        homepage = repo["website"] or (meta.get("homepage") or "").strip() if ok else repo["website"]
        if homepage and homepage.rstrip("/") == repo["url"].rstrip("/"):
            homepage = None
        out.append({
            "name": repo["name"],
            "url": repo["url"],
            "description": desc,
            "stars": (meta.get("stars") if ok else None) or repo["stars"] or 0,
            "license": lic,
            "homepage": homepage or None,
            "topics": (meta.get("topics") or [])[:6] if ok else [],
            "pushed": (meta.get("pushed") or "")[:10] if ok else "",
            "archived": bool(meta.get("archived")) if ok else False,
            "evidence": repo["evidence"],
            "unverified": repo["unverified"],
            "linux": repo["linux"],
            "category": CATEGORY_FIX.get(repo["name"], repo["category"]),
            "status": "ok" if ok else "unavailable",
        })

    live = [r for r in out if r["status"] == "ok"]
    live.sort(key=lambda r: (ORDER.get(r["category"], 99), -r["stars"], r["name"].lower()))

    payload = {
        "generated": "2026-11-02",
        "count": len(live),
        "repoUrl": config.get("repo", ""),
        "site": config.get("site", ""),
        "categories": [{"id": c, "title": t, "blurb": b,
                        "count": sum(1 for r in live if r["category"] == c)} for c, t, b in CATEGORIES],
        "repos": live,
    }
    SITE.parent.mkdir(parents=True, exist_ok=True)
    REPOS.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    (SITE.parent / "data.js").write_text(
        "window.MYGO = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    print("live", len(live), "unavailable", len(out) - len(live))
    print("stars total", sum(r["stars"] for r in live))
    print("no description", sum(1 for r in live if not r["description"]))


if __name__ == "__main__":
    main()
