# Changelog

## Unreleased

## 0.1.4

- **The two apps' main menu is one table.** `glossa.menu` holds the menu both readers open from their header as plain data, with no toolkit: Find; Appearance, Typography and Preferences; This note, Tabs and Show; Keyboard shortcuts and About. Each row carries its label, its action, and optionally a submenu or the capability a window must hold to offer it. `main_menu(capabilities, app)` returns the groups a window holding those capabilities keeps, so an editing row appears only where the window can edit and never by the name of the app, and `action_names` lists every action a menu names, so an app can test that its window registers each one. Each app builds its own menu from the groups. Preferences is a row the app fills itself, since one app opens a page and the other a dialog.

## 0.1.3

- **Stone by day has a white page and a neutral grey rail the eye can find.** The rail and the page were two warm greys 1.09:1 apart, with a hairline 1.14:1 from the rail, so the edge between them was lost. The page is white, the rail a neutral grey 1.27:1 from it, and the line between them 1.56:1 from the rail; a test holds the two floors, 1.25:1 and 1.5:1.

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
