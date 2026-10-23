# Privacy

The Ralphy plugin contains Markdown skills and reference documents only. It collects no
data, has no telemetry, and sends nothing to the Ralphy authors.

When you ask the agent to make content, it runs the open-source
[`ralphy` CLI](https://github.com/alecs5am/ralphy) on your machine. The CLI sends your
prompts and the reference media you supply to the model providers whose API keys you
configured (OpenRouter, ElevenLabs, and optionally fal, Firecrawl, and Apify). Those
providers' own privacy policies apply. Projects, generated media, and logs are stored
locally in a `.ralphy/` folder in your working directory.

Questions: open an issue at https://github.com/alecs5am/ralphy-plugin/issues.
