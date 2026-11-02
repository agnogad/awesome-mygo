# Contributing to Awesome MyGo

Thanks for helping keep this list accurate. It is small on purpose: every entry
should be a real, open-source project that a person could install and use today.

## What belongs here

- The project is **open source** and has a public repository.
- It **uses MyGo** — `github.com/egoist/mygo` — either for a native UI or as the
  desktop shell around a web frontend. A `go.mod` that requires MyGo is the
  strongest evidence; a fork of MyGo kept in the repository also counts.
- It is **not** a demo, a tutorial, or a fork with no changes.
- The description is one factual sentence in English. No "revolutionary",
  "blazingly fast", no emoji.

Closed-source apps, abandoned prototypes and repositories that were deleted are
removed from the list rather than kept for completeness.

## Adding an entry

The list is generated. `data/curated.json` is the source of truth; `README.md`
and `site/data.js` are built from it.

1. Add an object to `data/curated.json`:

   ```json
   {
     "name": "owner/repo",
     "url": "https://github.com/owner/repo",
     "description": "One sentence about what it does.",
     "stars": null,
     "license": null,
     "website": null,
     "evidence": "https://raw.githubusercontent.com/owner/repo/main/go.mod",
     "unverified": false,
     "linux": false,
     "category": "dev"
   }
   ```

   `stars`, `license` and `website` are filled in from the GitHub API, so `null`
   is fine. `evidence` is optional but appreciated — it is shown as a `go.mod`
   link in the "More Projects" section.

2. Pick a `category`: `author`, `ai`, `dev`, `writing`, `media`, `productivity`,
   `system`, `files`, `network`, `games`, `ui`, or `more`.
3. Run the build:

   ```sh
   make build
   ```

   This refreshes the merged dataset, rewrites `README.md` and rebuilds the site
   bundle. Commit all three.

If you would rather not touch JSON, open an issue with the repository link and a
sentence, and a maintainer will add it.

## Changing an existing entry

Edit the same object in `data/curated.json`. If a project stopped using MyGo or
its repository is gone, delete the object and mention why in the pull request.

## Refreshing metadata

Star counts, licenses and last-push dates are read from GitHub. With the
[GitHub CLI](https://cli.github.com/) authenticated:

```sh
python3 scripts/enrich.py   # refresh data/github.json
make build
```

The list is refreshed every few months; the date in the README and on the site
records when it last happened.

## Style

- Sentence case for descriptions, ending with a period.
- Name entries exactly as GitHub does (`owner/repo`), with the original casing.
- Keep the alphabetical/stars ordering that the build script produces; do not
  hand-sort sections.
