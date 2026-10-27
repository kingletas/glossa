"""The main menu both reading apps open from their header, as data.

The menu is one shape: Find; Appearance, Typography, Preferences; This note, Tabs, Show;
Keyboard shortcuts. Each app builds its own toolkit menu from this table, so the groups,
their order and their words cannot drift apart. Nothing here imports a toolkit.

An item only some windows can do carries `needs`, the name of a capability. The window passes
the set it holds to `main_menu`, which drops what it cannot do, so a menu offers an action
only where it works and never by the name of the app asking.

The capabilities the table asks for:

- `write`: the note can be edited, so it can be created, saved, undone, renamed and trashed.
- `find`: the open note has a find bar.
- `ask`: the open note can be asked about.
- `commands`: there is a command palette to open.
- `composition`: the window can say what it is made of.
- `export`: the note can be exported as a PDF.
- `files`: the note can be shown in the file manager and opened in another app.
- `reading-mode`: the window can go full screen with only the note in it.
- `focus-mode`: the window can put everything but the note away.
- `wrap`: long lines can be wrapped.
"""

from collections.abc import Collection
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Item:
    """One row, which is exactly one of: an action, a submenu, a custom widget or a leaf.

    `action` is a detailed action name such as `win.reload` or `win.appearance::dark`.
    `custom` names a widget the window puts into the row itself. `leaf` names a row whose
    destination differs by app, such as Preferences, which one app opens as a dialog and the
    other as a page of its own; the app says what it is. `needs` is a capability, or empty.
    """

    label: str
    action: str = ""
    submenu: tuple["Group", ...] = ()
    custom: str = ""
    leaf: str = ""
    needs: str = ""


@dataclass(frozen=True)
class Group:
    """Rows set apart from their neighbours, with a heading when `heading` is not empty."""

    items: tuple[Item, ...]
    heading: str = ""


def _choices(title: str, action: str, choices: tuple[tuple[str, str], ...]) -> Item:
    """A submenu of one-of-many rows that all drive one action with a target."""
    rows = tuple(Item(label, f"win.{action}::{value}") for label, value in choices)
    return Item(title, submenu=(Group(rows),))


APPEARANCE = (
    Group(
        (
            Item("Follow System", "win.appearance::system"),
            Item("Light", "win.appearance::light"),
            Item("Dark", "win.appearance::dark"),
        ),
        heading="Mode",
    ),
    Group((Item("", custom="themes"),), heading="Theme"),
)

TYPOGRAPHY = (
    Group(
        (
            _choices(
                "Font",
                "reader-font",
                (("Theme Default", "default"), ("Serif", "serif"), ("Sans", "sans"),
                 ("Mono", "mono")),
            ),
            _choices(
                "Line Width",
                "line-width",
                (("Narrow", "narrow"), ("Normal", "normal"), ("Wide", "wide"), ("Full", "full")),
            ),
            _choices(
                "Line Spacing",
                "line-spacing",
                (("Compact", "compact"), ("Normal", "normal"), ("Relaxed", "relaxed")),
            ),
        )
    ),
)

THIS_NOTE = (
    Group(
        (
            Item("New Note…", "win.new-note", needs="write"),
            Item("Find in This Note…", "win.find", needs="find"),
            Item("Line Up Tables", "win.align-tables", needs="write"),
            Item("Save", "win.save", needs="write"),
            Item("Undo", "win.undo", needs="write"),
            Item("Redo", "win.redo", needs="write"),
            Item("Rename…", "win.rename", needs="write"),
            Item("Move to Trash…", "win.delete", needs="write"),
            Item("Ask a Question…", "win.ask", needs="ask"),
            Item("Pin / Unpin Note", "win.pin"),
            Item("View as Mind Map", "win.mindmap"),
            Item("Export as PDF…", "win.export-pdf", needs="export"),
            Item("Reveal in Files", "win.reveal", needs="files"),
            Item("Open Externally", "win.open-external", needs="files"),
            Item(
                "Copy",
                submenu=(
                    Group(
                        (
                            Item("Markdown Source", "win.copy-source"),
                            Item("Vault Path", "win.copy-path"),
                            Item("As Wikilink", "win.copy-wikilink"),
                        )
                    ),
                ),
            ),
        )
    ),
)

TABS = (
    Group(
        (
            Item("New Tab", "win.new-tab"),
            Item("Close Tab", "win.close-tab"),
            Item("Reload", "win.reload"),
        )
    ),
)

SHOW = (
    Group(
        (
            Item("Reading Mode", "win.zen", needs="reading-mode"),
            Item("Focus Mode", "win.focus", needs="focus-mode"),
            Item("Vault Sidebar", "win.toggle-sidebar"),
            Item("On This Page", "win.toggle-outline"),
            Item("Raw Source View", "win.toggle-source"),
            Item("Wrap Long Lines", "win.wrap", needs="wrap"),
        )
    ),
)

MAIN_MENU = (
    Group(
        (
            Item("", custom="commands", needs="commands"),
            Item("Go to note…", "win.quick-open"),
            Item("Search the vault…", "win.search"),
        )
    ),
    Group(
        (
            Item("Appearance…", submenu=APPEARANCE),
            Item("Typography…", submenu=TYPOGRAPHY),
            Item("Preferences…", leaf="preferences"),
            Item("Composition…", "win.composition", needs="composition"),
        )
    ),
    Group(
        (
            Item("This note", submenu=THIS_NOTE),
            Item("Tabs", submenu=TABS),
            Item("Show", submenu=SHOW),
        )
    ),
    Group(
        (
            Item("Keyboard shortcuts", "win.shortcuts"),
            Item("About {app}", "win.about"),
        )
    ),
)


def main_menu(capabilities: Collection[str], app: str = "") -> tuple[Group, ...]:
    """The groups a window holding these capabilities offers, with `{app}` filled in.

    A row whose `needs` is not held is dropped, and so is a submenu or a group left empty by
    that, so a window never shows a heading or a drill-down with nothing behind it.
    """
    return _keep(MAIN_MENU, frozenset(capabilities), app)


def _keep(groups: tuple[Group, ...], held: frozenset[str], app: str) -> tuple[Group, ...]:
    kept: list[Group] = []
    for group in groups:
        items: list[Item] = []
        for item in group.items:
            if item.needs and item.needs not in held:
                continue
            if item.submenu:
                inner = _keep(item.submenu, held, app)
                if not inner:
                    continue
                item = replace(item, submenu=inner)
            items.append(replace(item, label=item.label.replace("{app}", app)))
        if items:
            kept.append(replace(group, items=tuple(items)))
    return tuple(kept)


def action_names(groups: tuple[Group, ...]) -> list[str]:
    """Every action the rows name, targets removed (`win.appearance::dark` is `win.appearance`)."""
    names: list[str] = []
    for group in groups:
        for item in group.items:
            if item.action:
                names.append(item.action.split("::", 1)[0])
            names.extend(action_names(item.submenu))
    return names
