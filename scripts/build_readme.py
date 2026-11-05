#!/usr/bin/env python3
"""Generate README.md from the merged dataset."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "repos.json").read_text(encoding="utf-8"))
CONFIG = json.loads((ROOT / "data" / "config.json").read_text(encoding="utf-8"))
SITE_URL = CONFIG["site"]
REPO_URL = CONFIG["repo"]

PICKS = [
    ("egoist/kero", "A terminal built for coding agents — sessions survive quitting, and agents can drive panes themselves."),
    ("egoist/mygo-cloudmusic", "A NetEase Cloud Music client with per-syllable lyrics and Hi-Res playback, drawn natively."),
    ("hyoban/peek", "A Git diff viewer where you can comment on lines and hand the comments to an agent as a prompt."),
    ("oneo-me/onevra", "A component library for MyGo native UI: themed controls, window shells, icons, charts and a command palette."),
    ("sorrycc/Mayoi", "A small, fast code editor with a GPU-drawn UI and no Electron in sight."),
    ("Binaryify/MonitorBar", "Switch monitor inputs and volume from the macOS menu bar or the Windows tray."),
]


def slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s", "-", text.strip())


def stars(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


def main() -> None:
    repos = DATA["repos"]
    by_name = {r["name"]: r for r in repos}
    total = len(repos)
    total_stars = sum(r["stars"] for r in repos)
    cats = [c for c in DATA["categories"] if c["count"]]

    lines: list[str] = []
    a = lines.append

    a('<div align="center">')
    a("")
    a("<h1>Awesome MyGo</h1>")
    a("")
    a("<p><strong>A curated list of desktop apps, tools and UI kits built with "
      '<a href="https://github.com/egoist/mygo">MyGo</a> — native Go UI, drawn on the GPU, no webview.</strong></p>')
    a("")
    a('<p><a href="https://awesome.re"><img alt="Awesome" src="https://awesome.re/badge-flat.svg"></a>')
    a(f'<img alt="Projects" src="https://img.shields.io/badge/projects-{total}-00ADD8?style=flat-square">')
    a(f'<img alt="Stars" src="https://img.shields.io/badge/stars-{stars(total_stars)}-7c6cf6?style=flat-square">')
    a('<img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-2ea44f?style=flat-square"></p>')
    a("")
    a(f'<p><strong><a href="{SITE_URL}">Browse the searchable site →</a></strong></p>')
    a("")
    a(f'<p><a href="{SITE_URL}"><img src="site/og.png" alt="Awesome MyGo — {total} native desktop apps built with Go" width="760"></a></p>')
    a("")
    a("</div>")
    a("")
    a("---")
    a("")
    a(
        "MyGo draws its own widgets on the GPU — no HTML, no JavaScript, no webview — so an app ships as a "
        "single Go binary of a few megabytes that opens instantly and sips memory. It also runs web frontends "
        "in the platform webview when you want one, and can mix both in the same window."
    )
    a("")
    a(
        f"This list collects what people have built with it: **{total} projects**, from terminals and coding "
        "agents to music players, Git clients, database GUIs and component libraries. Every entry links to a "
        "public repository, and star counts were refreshed from the GitHub API when this page was generated."
    )
    a("")

    # Contents
    a("## Contents")
    a("")
    a("- [What is MyGo?](#what-is-mygo)")
    a("- [Start here](#start-here)")
    for c in cats:
        a(f"- [{c['title']}](#{slug(c['title'])})")
    a("- [Notes on inclusion](#notes-on-inclusion)")
    a("- [Contributing](#contributing)")
    a("- [License](#license)")
    a("")

    # What is MyGo
    a("## What is MyGo?")
    a("")
    a(
        "[MyGo](https://github.com/egoist/mygo) is a toolkit for writing desktop apps in Go. A window can show "
        "a native UI written in Go alone, or a web page in the webview the OS already has — and one app can mix "
        "the two."
    )
    a("")
    a("- **Native UI** — flexbox and grid layout, widgets, text editing with input methods, virtualized lists, SVG icons, animations and screen-reader support, all drawn by MyGo.")
    a("- **Pure Go, no cgo** — cross-compile for macOS, Windows and Linux from any machine.")
    a("- **Desktop APIs** — windows, menus, tray, dialogs, notifications, global shortcuts, deep links, file associations and auto-updates.")
    a("- **Ready to ship** — app bundles, DMGs, Windows installers, Debian packages, Arch PKGBUILDs, signing and notarization.")
    a("")
    a("A window with a native UI is a Go function of the app's state:")
    a("")
    a("```go")
    a("type counter struct{ n int }")
    a("")
    a("func (s *counter) view(c *ui.Context) {")
    a("\tui.Column(c).Fill().Center().Gap(12).Children(func() {")
    a('\t\tui.Text(c, fmt.Sprint(s.n)).FontSize(40).Bold()')
    a('\t\tif ui.PrimaryButton(c, "Increment").Clicked() {')
    a("\t\t\ts.n++")
    a("\t\t}")
    a("\t})")
    a("}")
    a("")
    a("func main() {")
    a("\ts := &counter{}")
    a("\tmygo.App.WhenReady(func() {")
    a("\t\tmygo.NewWindow(mygo.WindowOptions{")
    a('\t\t\tTitle:   "Counter",')
    a("\t\t\tContent: ui.View(s.view),")
    a("\t\t})")
    a("\t})")
    a("\tif err := mygo.App.Run(); err != nil {")
    a("\t\tlog.Fatal(err)")
    a("\t}")
    a("}")
    a("```")
    a("")
    a("```sh")
    a("go run github.com/egoist/mygo/cmd/mygo@latest init -template native my-app")
    a("```")
    a("")
    a("Read the [MyGo documentation](https://github.com/egoist/mygo) to go further.")
    a("")

    # Start here
    a("## Start here")
    a("")
    a("Six projects that show what the toolkit feels like in practice:")
    a("")
    for name, blurb in PICKS:
        r = by_name.get(name)
        if not r:
            continue
        a(f"- **[{name}]({r['url']})** — {blurb} <sub>★ {stars(r['stars'])}</sub>")
    a("")

    # Sections
    for c in cats:
        items = [r for r in repos if r["category"] == c["id"]]
        a(f"## {c['title']}")
        a("")
        a(f"<sub>{c['blurb']} · {len(items)} project{'s' if len(items) != 1 else ''}</sub>")
        a("")
        for r in items:
            meta = []
            if r["stars"]:
                meta.append(f"★ {stars(r['stars'])}")
            if r["license"]:
                meta.append(r["license"])
            if r["evidence"]:
                meta.append(f"[go.mod]({r['evidence']})")
            if r["unverified"]:
                meta.append("unverified")
            suffix = f" <sub>{' · '.join(meta)}</sub>" if meta else ""
            a(f"- **[{r['name']}]({r['url']})** — {r['description']}{suffix}")
        a("")

    # Notes
    a("## Notes on inclusion")
    a("")
    a("- A project is listed when its repository depends on `github.com/egoist/mygo`, either directly or through a fork kept in the project.")
    a("- A `go.mod` link in the metadata opens the file that proves the dependency, at the path where it lives in that repository.")
    a("- The **unverified** marker means the source list could not confirm the dependency from a `go.mod` file at review time.")
    a("- Star counts, licenses and last-push dates were read from the GitHub API on **5 November 2026** and are rounded.")
    a("- Six entries from the research returned `404` on GitHub and are not listed here: `yaffalhakim1/opencode-gui`, `my3rs/GoShell`, `diver80/avono-timebooking`, `oscs1024-pixel/MiJia`, `ychuo/copiggy` and `gahulv/mygo-notes`.")
    a("- Most listed repositories are open source, but not all: PudMusic is under PolyForm Noncommercial and vibe-cook under BUSL-1.1, both of which restrict production use. Check each project's license before reusing it.")
    a("- Closed-source apps are out of scope, with one exception noted in the source material: the author's own Pulse is not listed because its source is not public.")
    a("- This is a living list, not a ranking. Alphabetical order within a section would be just as fair; the current order is by stars, for browsing.")
    a("")
    a("## Contributing")
    a("")
    a(f"Found something missing, or a project that no longer uses MyGo? [Open a pull request or an issue]({REPO_URL}/issues), or edit the entry directly.")
    a("")
    a("```markdown")
    a("- **[owner/repo](https://github.com/owner/repo)** — One sentence, in English, about what it does.")
    a("```")
    a("")
    a("Please keep the sentence factual and free of marketing language, add the entry to the section that fits best, and mention how the project uses MyGo. See [CONTRIBUTING.md](CONTRIBUTING.md) for the details.")
    a("")
    a("## License")
    a("")
    a("[MIT](LICENSE) for this list. Each project keeps its own license — check the repository before you reuse anything.")
    a("")

    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print("README.md written:", len(lines), "lines")


if __name__ == "__main__":
    main()
