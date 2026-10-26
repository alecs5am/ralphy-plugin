# Ralphy

Ralphy turns your coding agent into a content studio. You describe what you want in plain
language (a UGC ad for your product, a poster, a 7-slide carousel, a pack of Meta ad
creatives, short clips cut from a long video, a faceless explainer from a podcast), and the
agent drives the open-source [`ralphy` CLI](https://github.com/alecs5am/ralphy) to research,
write the script, generate images, video, voice and music, render the final cut, score it
against quality gates, and package the finished deliverable.

This plugin carries the know-how: a routing skill (`ralphy`) plus production-role and
content-format skills (intake, scenarist, art-director, editor, producer, researcher,
evaluator, fixer, poster, carousel, fb-creatives, ugc-ad, personal-clipper, and more), and
the reference docs those skills read (model picks, CLI cheatsheet, production contract,
prompt guidelines).

## Requirements

- The `ralphy` CLI: `brew install alecs5am/tap/ralphy` (macOS) or
  `npm install -g @alecs5am/ralphy`. The `install` skill walks through it.
- CLI 0.4.0 or newer, initialized with `ralphy setup --non-interactive`; no source checkout is required.
- Your own provider keys, exported before the CLI starts or stored with scoped `provider auth set <provider> --stdin`: OpenRouter (images, video, LLM)
  and ElevenLabs (voice, music). fal, Firecrawl, and Apify are optional.
- `ffmpeg` and `bun` on your machine (the CLI checks with `ralphy doctor`).

## What the plugin runs, sends, and stores

The plugin itself contains only Markdown skills, reference docs, and an icon. It has no
hooks, no MCP servers, no bundled executables, and no telemetry. Everything happens through
the `ralphy` CLI, which the agent runs on your machine when you ask for content:

- **Model providers you configure.** Prompts, reference images, and audio you supply are
  sent to the providers whose keys you set: OpenRouter (`openrouter.ai`), ElevenLabs
  (`api.elevenlabs.io`), and optionally fal (`fal.ai`, `queue.fal.run`). Their own terms and
  privacy policies apply. Every call is billed to your account; the skills require a cost
  preview and your explicit go before any paid generation.
- **Research.** When you give a URL or ask for research, the CLI fetches public pages and
  media you point at (for example YouTube, TikTok, or Instagram via yt-dlp), searches
  DuckDuckGo, and, if you configured them, calls Firecrawl (`api.firecrawl.dev`) or Apify
  (`api.apify.com`).
- **Public content.** The CLI downloads the public template library from
  `ralphy.b-cdn.net` and optional template assets from GitHub (`raw.githubusercontent.com`).
  These are read-only downloads; nothing about you is sent.
- **Publishing.** The CLI can post to blogs or social accounts (for example Hashnode, DEV,
  or a Postiz connection) only when you configure that destination and explicitly ask to
  publish.
- **Local storage.** Projects, generated media, prompts, and logs stay on your machine in a
  hidden `.ralphy/` folder in your working directory or an explicit local data root.
  Persisted provider keys use a scoped encrypted store backed by macOS Keychain;
  inherited shell keys remain process-local. Nothing is uploaded to the Ralphy authors.

## Source

Generated from [alecs5am/ralphy](https://github.com/alecs5am/ralphy); `SOURCE.json` records
the exact commit. Licensed under Apache-2.0.
