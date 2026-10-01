<h1 align="center">glossa</h1>

<p align="center">The Obsidian dialect, rendered read-only in pure Python.</p>

---

Obsidian notes are Markdown with a dialect on top: wikilinks and embeds, callouts, frontmatter, Dataview queries, `.base` views, canvases, Kanban boards, Excalidraw drawings and Mermaid diagrams. This library reads each of those in pure Python, without running anything a note contains. Queries, bases, canvases, boards and drawings come out as escaped HTML. Markdown comes out as tokens, with every link and embed already taken apart, so each app draws them its own way.

It is the rendering core two reading apps share: [Solander](https://github.com/kingletas/solander), a read-only vault reader, and Slate. Both used to carry their own copy of these modules, kept identical by a check that ran only when both checkouts were on one machine. Every fix was made twice. Now it is made here once, and each app pins a version.

## What it promises

- **It never writes.** No module opens a file for writing, and none keeps a cache on disk.
- **It never runs a note's code.** A Dataview query is evaluated by a small interpreter written here, and nothing in the library calls `eval`, `exec` or a subprocess. What an app shows for a `dataviewjs` block is the app's choice.
- **It never touches the network.** Every link it renders points into the vault or is left for the app to decide.
- **Everything it renders as HTML is escaped**, and every limit is a number you can read: listed under [Limits](#limits) and set by environment variable.

## What is in it

| Module | What it does |
|---|---|
| `markdown`, `links`, `callouts`, `frontmatter` | Parse CommonMark and GFM with Obsidian's links, embeds, callouts and properties into tokens; the app renders them |
| `dql`, `dataview` | Evaluate Dataview's query language and inline expressions, and render a query's table or list |
| `bases` | Render `.base` table views: filters, formulas, groups and row limits |
| `canvas`, `kanban`, `excalidraw`, `lzstring`, `mermaid` | Render canvases, boards, drawings and diagrams |
| `fuzzy`, `listdiff`, `palettes` | Fuzzy matching, list diffs, and the color palettes both apps theme with |

`dataview` and `bases` ask the app for a vault graph: an object with `props`, `outgoing`, `backlinks`, `note_tags`, `tasks` and `meta`. Each app builds its own. A graph must not be changed in place once built, because the file fields of each note are cached on it.

## Using it

It is not on PyPI. An app depends on a tagged version straight from this repository:

```toml
dependencies = [
    "glossa[render] @ git+https://github.com/kingletas/glossa@v0.1.0",
]
```

A bare `glossa` is the standard library alone, and covers every module but three. `markdown`, `frontmatter` and `bases` parse Markdown or read YAML, so they need the `render` extra, which brings markdown-it-py, its plugins, linkify-it-py and PyYAML. An app that only themes with the palettes or diffs lists can leave the extra off.

## Limits

Each limit is read from the environment once, when its module is first imported, so set it before then. Past a limit, some input is refused with a message and some is cut without one, as the last column says.

| Variable | Default | Caps | Past it |
|---|---|---|---|
| `READER_MAX_FRONTMATTER_BYTES` | 128 KiB | A note's properties block | The note has no properties |
| `READER_MAX_BASE_BYTES` | 1 MiB | A `.base` file | Refused, with a message |
| `READER_MAX_CANVAS_BYTES` | 5 MiB | A canvas file | Refused, with a message |
| `READER_MAX_CANVAS_NODES` | 1,000 | The cards on one canvas | The first 1,000 are drawn, silently |
| `READER_MAX_DRAWING_BYTES` | 10 MiB | An Excalidraw drawing | Refused, with a message |
| `READER_MAX_DRAWING_ELEMENTS` | 3,000 | The shapes in one drawing | The first 3,000 are drawn, silently |
| `READER_MAX_DIAGRAM_NODES` | 400 | The nodes in one Mermaid diagram | `MermaidError`, for the app to show |

Versions follow semantic versioning from `0.1.0`. While the major version is 0, a minor release may change what a module renders, and the CHANGELOG says how.

## Developing it

```bash
make check
```

Runs ruff and the tests. The tests here cover what needs no vault. Each app keeps the tests that need its own vault graph, so a change here is proved in both apps before it is tagged.

## Licence

MIT. See [LICENSE](LICENSE).
