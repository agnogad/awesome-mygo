#!/usr/bin/env python3
"""Render site/og.png (1200x630 @2x) from the live dataset."""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "repos.json").read_text(encoding="utf-8"))

total = DATA["count"]
stars = sum(r["stars"] for r in DATA["repos"])
stars = f"{stars / 1000:.1f}k".replace(".0k", "k")
cats = sum(1 for c in DATA["categories"] if c["count"])

HTML = f"""<!doctype html>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  html, body {{ width: 1200px; height: 630px; overflow: hidden; }}
  body {{
    background:
      radial-gradient(620px 320px at 50% 40%, rgba(110, 231, 255, .10), transparent 70%),
      radial-gradient(900px 480px at 50% 52%, rgba(167, 139, 250, .10), transparent 72%),
      #08090c;
    color: #f5f7fa;
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    display: flex; flex-direction: column; align-items: center;
    position: relative;
  }}
  body::before {{
    content: ""; position: absolute; inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
    background-size: 60px 60px;
    -webkit-mask-image: radial-gradient(ellipse 70% 65% at 50% 50%, #000 30%, transparent 100%);
  }}
  .logo {{ width: 104px; height: 104px; margin-top: 150px; filter: drop-shadow(0 0 34px rgba(110,231,255,.35)); }}
  h1 {{ margin-top: 40px; font-size: 96px; font-weight: 800; letter-spacing: -2.5px; }}
  h1 span {{ background: linear-gradient(90deg, #6ee7ff 10%, #a78bfa 90%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
  p {{ margin-top: 22px; font-size: 32px; font-weight: 400; color: #9aa3b4; letter-spacing: .2px; }}
  footer {{ position: absolute; bottom: 48px; font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 20px; color: #6f7787; letter-spacing: .5px; }}
</style>
<svg class="logo" viewBox="0 0 32 32" aria-hidden="true">
  <rect width="32" height="32" rx="9" fill="url(#g)"/>
  <path d="M8 22V10l8 7 8-7v12" stroke="#08090c" stroke-width="3" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
  <defs><linearGradient id="g" x1="0" y1="0" x2="32" y2="32"><stop offset="0" stop-color="#6ee7ff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>
</svg>
<h1>Awesome <span>MyGo</span></h1>
<p>{total} native desktop apps, tools and UI kits built with Go.</p>
<footer>awesome-mygo.surge.sh · {stars} stars · {cats} categories</footer>
"""

with tempfile.TemporaryDirectory() as tmp:
    page = Path(tmp) / "og.html"
    page.write_text(HTML, encoding="utf-8")
    subprocess.run([
        "chromium", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", "--window-size=1200,630",
        f"--screenshot={ROOT / 'site' / 'og.png'}", page.as_uri(),
    ], check=True, capture_output=True, timeout=120)

print("og.png:", total, "projects,", stars, "stars,", cats, "categories")
