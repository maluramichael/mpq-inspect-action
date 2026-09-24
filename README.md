# mpq-inspect-action

A reusable GitHub Action that **opens the MPQ files changed in a pull request,
decodes what's inside, and posts a Markdown summary as a sticky PR comment** — so
you can review a WoW client patch without downloading and unpacking it by hand.

Built for [AzerothCore](https://www.azerothcore.org/) / 3.3.5a client patches
(`patch-*.MPQ`), where the interesting payload is usually a handful of DBC files.

## What it reports

- **File manifest** — every file inside each changed `.MPQ` and its size.
- **`CharBaseInfo.dbc`** — decoded race/class combos, **diffed against the
  standard WotLK matrix**, so newly enabled combos (e.g. *Gnome Priest*,
  *Human Hunter*) are highlighted.
- **Any other `.dbc`** — WDBC header stats (records / fields / record size).
- **Text files** (`.lua`, `.xml`, `.toc`, `.txt`, …) — a short preview.
- Unknown binaries just appear in the manifest.

## Usage

Add one workflow to the repo that receives MPQ PRs (see
[`examples/workflow.yml`](examples/workflow.yml)):

```yaml
name: Inspect MPQ patches
on:
  pull_request_target:
    types: [opened, synchronize, reopened]
    paths: ["**/*.MPQ", "**/*.mpq"]
  workflow_dispatch:
    inputs:
      pr: { description: "PR number to inspect", required: true }
permissions:
  contents: read
  pull-requests: write
jobs:
  inspect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          repository: ${{ github.event.pull_request.head.repo.full_name || github.repository }}
          ref: ${{ github.event.pull_request.head.sha || format('refs/pull/{0}/head', github.event.inputs.pr) }}
          persist-credentials: false
      - uses: maluramichael/mpq-inspect-action@main
        with:
          pr-number: ${{ github.event.pull_request.number || github.event.inputs.pr }}
```

Pin to `@main` for always-latest (no tag bumping), or to a release tag if you
want to freeze a version.

### Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `pr-number` | current PR | PR to inspect / comment on |
| `repository` | current repo | `owner/name` for the PR files API |
| `files` | _(auto)_ | explicit MPQ paths; otherwise changed `*.mpq` are auto-detected |
| `max-mb` | `10` | skip archives larger than this |
| `comment` | `true` | post/update the sticky comment |
| `comment-header` | `mpq-inspect` | sticky-comment identity |
| `github-token` | `github.token` | token for the API + comment |

### Output

- `report` — the generated Markdown (use it in later steps if you don't want the
  built-in comment).

## Why `pull_request_target`?

Fork PRs get a **read-only** token under `pull_request`, so the action couldn't
comment. `pull_request_target` runs in the base repo's context with a writable
token. It is safe here because the action **only reads the PR's binary MPQ as
data and runs its own code from the base repo** — it never checks out or executes
anything from the PR (`persist-credentials: false`, no build steps).

## Extending it

Decoders are pluggable. To support another file that shows up inside MPQs:

1. Add a module under `src/decoders/` with a class exposing
   `matches(filename) -> bool` and `render(filename, data) -> str | None`.
2. Register an instance in `src/decoders/__init__.py` (`DECODERS`, most specific
   first).

`src/mpq_reader.py` isolates the MPQ loader ([mpyq](https://github.com/eagleflo/mpyq),
MIT). If a patch ever uses a compression mpyq can't read, swap that one file for a
[StormLib](https://github.com/ladislav-zezula/StormLib)-backed reader (`apt install smpq`)
— nothing else changes.

## License

MIT — see [LICENSE](LICENSE).
