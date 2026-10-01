# From nothing to a working glossa

By the end of this, you will have read a note's properties, parsed its links and evaluated a Dataview expression against it, in about ten lines of Python.

## What this is

glossa reads Obsidian's dialect of Markdown without running anything a note contains. You give it text; it gives you properties, tokens with every link taken apart, or escaped HTML for queries, bases, canvases, boards and drawings. Drawing a link or a callout is left to your app, because two apps rarely want the same anchor.

## Step 1: install it

Into the project that will use it:

```bash
uv add "glossa @ git+https://github.com/kingletas/glossa@v0.1.0"
```

## Step 2: read a note

```python
from glossa.dataview import Evaluator, Row
from glossa.dql import parse_expression
from glossa.frontmatter import split_frontmatter
from glossa.markdown import build_parser

note = split_frontmatter("---\nstatus: open\npriority: 2\n---\nSee [[Projects/Alpha]].\n")
print(note.properties)

for token in build_parser().parse(note.body):
    for child in token.children or []:
        if child.type == "obsidian_wikilink":
            print(child.meta["link"])

row = Row(note.properties, {})
print(Evaluator().evaluate(parse_expression('choice(priority > 1, "soon", "later")'), row))
```

## Step 3: run it

This is the output of that script, copied from a real run:

```text
{'status': 'open', 'priority': 2}
WikiLink(target='Projects/Alpha', anchor='', block_id='', alias='', size='')
soon
```

The properties came out typed, the link came out as its parts rather than as HTML, and the expression was answered by glossa's own interpreter.

## What you get for free

- **Obsidian's link grammar**: targets, headings, block ids, aliases and embed sizes, already split.
- **A Dataview interpreter** that answers the query language and inline expressions in Python, with no JavaScript anywhere.
- **Limits on everything large**: a base, a canvas, a drawing or a diagram past its limit is refused or cut, and the output says which.

## Where to go next

- [README](../README.md), for the modules and the vault graph `dataview` and `bases` ask for
- [CONTRIBUTING.md](../CONTRIBUTING.md)
