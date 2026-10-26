<h1 align="center">glossa</h1>

<p align="center">The Obsidian dialect, rendered read-only in pure Python.</p>

---

Obsidian notes are Markdown with a dialect on top: wikilinks and embeds, callouts, frontmatter, Dataview queries, `.base` views, canvases, Kanban boards, Excalidraw drawings and Mermaid diagrams. This library reads each of those in pure Python, without running anything a note contains. Queries, bases, canvases, boards, drawings and diagrams come out as escaped HTML. Markdown comes out as tokens, with every link and embed already taken apart, so each app draws them its own way.

It's the rendering core of [Solander](https://github.com/kingletas/solander), a read-only vault reader, and of a second reading app. Each pins a version.

## What it promises

- **It never writes.** No module opens a file for writing, and none keeps a cache on disk.
- **It never runs a note's code.** A Dataview query is evaluated by a small interpreter written here, and nothing in the library calls `eval`, `exec` or a subprocess. What an app shows for a `dataviewjs` block is the app's choice.
- **It never touches the network.** It fetches nothing. An image or a link keeps the address the note wrote, and whether to load it is the app's choice.
- **Everything it renders as HTML is escaped.** A note is treated as hostile: every size it can drive has a limit, listed under [Limits](#limits).

## What the app has to do

- **Decide what a link may open.** A link or embed target is passed through as the note wrote it, `../` and absolute paths included, so the app's handler for it must keep it inside the vault.
- **Escape what it draws from tokens and errors.** Token fields, `DqlError` and `MermaidError` messages carry the note's own text.
- **Catch each renderer's one error.** `DataviewEngine.run_query` and `run_inline` raise `DqlError`, and `render_mermaid` raises `MermaidError` (or `MermaidUnsupported` for a diagram type it does not draw). Whatever a note trips inside them arrives as that error. `render_base` never raises; it returns a message in markup.
- **Register callouts if it wants them.** `build_parser` leaves them out, so an app adds them: `md.core.ruler.before("inline", "obsidian_callouts", callouts_rule)`.

## What is in it

| Module | What it does |
|---|---|
| `markdown`, `links`, `callouts`, `frontmatter` | Parse CommonMark and GFM with Obsidian's links, embeds, callouts and properties into tokens; the app renders them |
| `dql`, `dataview` | Evaluate Dataview's query language and inline expressions, and render a query's table or list |
| `bases` | Render `.base` table views: filters, formulas, groups and row limits |
| `canvas`, `kanban`, `excalidraw`, `lzstring`, `mermaid` | Render canvases, boards, drawings and diagrams |
| `fuzzy`, `listdiff`, `palettes` | Fuzzy matching, list diffs, and the color palettes both apps theme with |

`dataview` and `bases` ask the app for a vault graph. Each app builds its own, keyed by each note's path inside the vault:

| Member | Holds |
|---|---|
| `props` | path to the note's properties, a dict |
| `outgoing` | path to the links the note makes, each with `.kind`, `.path` and `.target` |
| `backlinks` | path to the links into the note, each with `.source` |
| `note_tags` | path to the note's tags |
| `tasks` | path to the note's tasks, each a `(status, text)` pair |
| `meta` | path to `(mtime, size)` |
| `notes_tagged(tag)` | a method: the paths of the notes carrying a tag, for `FROM #tag` |

A graph must not be changed in place once built, because the file fields of each note are cached on it.

## Using it

It needs Python 3.12 or later, and isn't on PyPI. An app depends on a tagged version straight from this repository:

```toml
dependencies = [
    "glossa[render] @ git+https://github.com/kingletas/glossa@v0.1.1",
]
```

A bare `glossa` is the standard library alone, and covers every module but three. `markdown`, `frontmatter` and `bases` parse Markdown or read YAML, so they need the `render` extra, which brings markdown-it-py, its plugins, linkify-it-py and PyYAML. An app that only themes with the palettes or diffs lists can leave the extra off.

## Limits

Each limit is read from the environment once, when its module is first imported, so set it before then. A value that isn't a whole number stops the module importing. Past a limit, some input is refused with a message and some is cut without one, as the last column says.

| Variable | Default | Caps | Past it |
|---|---|---|---|
| `READER_MAX_FRONTMATTER_BYTES` | 128 KiB | A note's properties block | The note has no properties |
| `READER_MAX_BASE_BYTES` | 1 MiB | A `.base` file | Refused, with a message |
| `READER_MAX_CANVAS_BYTES` | 5 MiB | A canvas file | Refused, with a message |
| `READER_MAX_CANVAS_NODES` | 1,000 | The cards on one canvas | The first 1,000 are drawn, silently |
| `READER_MAX_DRAWING_BYTES` | 10 MiB | An Excalidraw drawing's JSON, counted in characters while it is decompressed | Refused, with a message |
| `READER_MAX_DRAWING_ELEMENTS` | 3,000 | The elements read from one drawing | The first 3,000 are read, silently, and deleted ones among them are skipped |
| `READER_MAX_DIAGRAM_NODES` | 400 | A flowchart's nodes, a sequence diagram's participants, a pie's slices | `MermaidError`, for the app to show |
| `READER_MAX_DIAGRAM_EDGES` | 2,000 | A flowchart's edges (`A & B --> C & D` adds every pair), a sequence diagram's messages and notes | `MermaidError`, for the app to show |
| `READER_MAX_VALUE_CHARS` | 1,000,000 | The longest string or list one Dataview or base expression builds | `DqlError` |

Two caps are fixed in the code: a Dataview query draws its first 2,000 rows and a base view its first 500, each with a note saying so. A base view's own `limit` can lower that, never raise it.

A properties block or a `.base` file that uses YAML aliases (`*name`) is not read at all: a few lines of them can expand to gigabytes. The note has no properties, and the base shows a message.

Versions follow semantic versioning from `0.1.0`. While the major version is 0, a minor release may change what a module renders, and the CHANGELOG says how.

## Developing it

```bash
make check
```

Runs ruff and the tests, with [uv](https://docs.astral.sh/uv/). CI also runs semgrep over the source and the tests, on Python 3.12 and 3.13.

The tests cover links, frontmatter, canvases, drawings and their decompression, fuzzy matching, list diffs, Dataview expressions, the limits a hostile note runs into, and a bare install. `markdown`, `callouts`, `kanban`, `palettes`, Mermaid's layout and most of `bases` have no test here yet.

## Licence

MIT. See [LICENSE](LICENSE).
