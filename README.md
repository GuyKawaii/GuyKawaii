<div align='center'>
  <img src='out/fetch.gif' alt='Github Fetch'>
</div>

A TypeScript pipeline generates this cyberpunk profile card daily. The portrait
uses HTML canvas with original avatar colors, noise and twinkle. Neofetch-style
information is configured in `profile_info` in `config.json`.

`Repositories LOC` counts the default branch of all owned public and private repos,
including forks and archived repos, excluding comments, blank lines, common build
outputs and dependencies. Public repos and stars describe public activity.
Repository Commits combines default-branch history from public and private owned
repositories, including archived ones but excluding forks. It includes all authors
and bots, with no date limit. Only the combined total is published.

## Local development

Use Bun 1.4.4 or later (CI is pinned to 1.4.4):

```sh
bun install --frozen-lockfile
bun run --bun playwright install chromium
bun run preview
```

The preview uses an embedded public avatar and illustrative values from
`fixtures/profile.json`; it needs no token or GitHub access. Open
`out/typescript-preview/fetch.gif` or `fetch.png`. Changes to the layout or effects
can be previewed without collecting repository statistics.

```sh
bun run check
bun test app/
```

## Updating real statistics

Install `cloc` on PATH, then set `GH_TOKEN` in your environment:

```sh
bun run collect
bun run render
# Or run both:
bun run update
```

Collection writes `.cache/profile.json`, containing only allowlisted aggregate
values and the embedded public avatar. Local per-repository count caches reuse
unchanged default-branch commit SHAs. No cache is committed or uploaded. A collection
failure stops the update instead of publishing an incomplete total. Source archives
are removed after counting. Raw API errors containing repository details are hidden.

In GitHub Actions, save the fine-grained token as `GH_TOKEN`, with all owned
repositories selected and read-only Contents, Issues, Pull requests and Metadata.
No expiration can be selected. The built-in `GITHUB_TOKEN` publishes the exports;
the personal token has no write permissions.

## Architecture

- `app/collect.ts`: GitHub access, temporary source scanning, count cache.
- `app/model.ts`: typed snapshot and public-field allowlist.
- `app/browser.ts`: Neofetch layout; no GitHub credentials or network access.
- `app/portrait.ts`: deterministic, source-color noise and twinkle effect.
- `assets/ascii-portrait.html`: static canvas host; no application logic.
- `app/render.ts`: browser rendering and PNG/GIF exports using a shared palette.
- `app/cli.ts`: independent collect, render, preview and update commands.

Bun runs TypeScript directly, with `bun.lock` for reproducible dependency installs.
The runtime is entirely TypeScript; the previous Python implementation remains
available in Git history.
