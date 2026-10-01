"""What a bare install can import: every module but the three the `render` extra is for."""

import importlib
import sys

import pytest

RENDER_PACKAGES = ["markdown_it", "mdit_py_plugins", "linkify_it", "yaml"]

BARE_MODULES = [
    "callouts",
    "canvas",
    "dataview",
    "dql",
    "excalidraw",
    "fuzzy",
    "kanban",
    "links",
    "listdiff",
    "lzstring",
    "mermaid",
    "palettes",
]

NEEDS_RENDER = ["bases", "frontmatter", "markdown"]


@pytest.fixture
def without_render_extra(monkeypatch):
    """Makes the extra's packages unimportable, and forgets any glossa module already loaded."""
    for name in list(sys.modules):
        if name.split(".")[0] in RENDER_PACKAGES or name.startswith("glossa."):
            monkeypatch.delitem(sys.modules, name)
    for package in RENDER_PACKAGES:
        monkeypatch.setitem(sys.modules, package, None)


@pytest.mark.parametrize("module", BARE_MODULES)
def test_a_bare_install_imports_it(without_render_extra, module):
    importlib.import_module(f"glossa.{module}")


@pytest.mark.parametrize("module", NEEDS_RENDER)
def test_it_needs_the_render_extra(without_render_extra, module):
    with pytest.raises(ImportError):
        importlib.import_module(f"glossa.{module}")
