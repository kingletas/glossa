# Changelog

## Unreleased

## 0.1.2

- **The palettes catch up with the apps.** `Palette.legible()` takes several grounds and lifts a colour until it clears all of them; `Palette.card` names the surface a card or dialog sits on; `Palette.chrome_muted` is the quiet label colour lifted to 4.5:1 on the canvas, the rail and a card. `channels()` is public, for an app that builds its own colours from a palette.

## 0.1.1

- **A note can no longer make a reader run out of memory.** Three small files could each take gigabytes: a `.base` file of YAML aliases (now refused, as frontmatter's already were), an Excalidraw drawing that decompresses far past its size cap (now stopped as it passes the cap, not after), and a Dataview expression that nests `replace()` (now refused past `READER_MAX_VALUE_CHARS`). Mermaid flowcharts gain an edge cap, `READER_MAX_DIAGRAM_EDGES`, and sequence diagrams and pies are held to the node cap.
- **Each renderer raises only its own error.** Whatever a note trips inside a query, an inline expression or a diagram reaches the app as `DqlError` or `MermaidError`; a base file shows a message.
- A base view sorts numbers by value, so 2 comes before 10.
- A canvas card at `NaN` or infinity is skipped like any other unreadable card.
- The release workflow runs the tests with a read-only token, and only its publishing job can write.
- The README names what an app must do itself, the whole vault graph, and every limit.
- The minimum versions of markdown-it-py, mdit-py-plugins, linkify-it-py and PyYAML are raised to 4.2.0, 0.6.1, 2.2.0 and 6.0.3.

## 0.1.0

The first release: fifteen rendering modules, with the tests that need no vault.

A bare install needs nothing past the standard library. Parsing Markdown and reading YAML take the `render` extra, so an app that only uses the palettes or the list diffs installs no Markdown parser. The README lists every `READER_MAX_*` limit with its default.
