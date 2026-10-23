# Ralphy plugin

Agent plugin for [Ralphy](https://github.com/alecs5am/ralphy), the open-source content farm
for coding agents. It teaches Claude Code, Claude, and Codex to make AI UGC videos, ads,
posters, carousels, ad packs, clips, and explainers through the `ralphy` CLI.

The plugin lives in [`plugins/ralphy/`](plugins/ralphy/). Its
[README](plugins/ralphy/README.md) describes what it runs, what it sends where, and what it
stores. Privacy: [PRIVACY.md](PRIVACY.md).

## Install

Claude Code:

```bash
claude plugin marketplace add alecs5am/ralphy-plugin
claude plugin install ralphy@ralphy
```

Codex:

```bash
codex plugin marketplace add alecs5am/ralphy-plugin
```

Then install the CLI the skills drive: `brew install alecs5am/tap/ralphy` or
`npm install -g @alecs5am/ralphy`.

## Layout

| Path | Purpose |
|---|---|
| `plugins/ralphy/` | The plugin: skills, reference docs, manifests for Claude (`.claude-plugin/`) and Codex (`.codex-plugin/`) |
| `.claude-plugin/marketplace.json` | Claude Code marketplace entry |
| `.agents/plugins/marketplace.json` | Codex marketplace entry |
| `src/` | Hand-written plugin files: manifests, README, icon, the `ralphy` routing skill |
| `build.py`, `sync.sh` | Rebuild `plugins/ralphy/` from the Ralphy repository |

## Updating from Ralphy

Skills and reference docs are generated from committed files in the Ralphy repository, so
uncommitted work in a local checkout never leaks in:

```bash
./sync.sh ../ralphy origin/main
```

`plugins/ralphy/SOURCE.json` records the source commit. Bump `version` in both manifests
under `src/` before publishing a new release.

## License

Apache-2.0, same as Ralphy.
