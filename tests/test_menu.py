"""The main menu's table: its first level, what a capability adds, and that words are shared."""

import pytest

from glossa.menu import MAIN_MENU, Group, Item, action_names, main_menu

EVERYTHING = {
    "write", "find", "ask", "commands", "composition", "export", "files",
    "reading-mode", "focus-mode", "wrap",
}


def labels(groups: tuple[Group, ...]) -> list[list[str]]:
    return [[item.label for item in group.items] for group in groups]


def walk(groups: tuple[Group, ...]):
    for group in groups:
        for item in group.items:
            yield item
            yield from walk(item.submenu)


def test_the_first_level_is_find_then_settings_then_the_note_then_help():
    assert labels(main_menu(set(), app="Reader")) == [
        ["Go to note…", "Search the vault…"],
        ["Appearance…", "Typography…", "Preferences…"],
        ["This note", "Tabs", "Show"],
        ["Keyboard shortcuts", "About Reader"],
    ]


def test_an_item_only_some_windows_can_do_is_dropped_without_its_capability():
    plain = labels(main_menu(set()))
    assert "New Note…" not in [row for group in plain for row in group]
    note = next(item for item in main_menu(set())[2].items if item.label == "This note")
    assert [i.label for i in note.submenu[0].items] == [
        "Pin / Unpin Note", "View as Mind Map", "Copy"
    ]


def test_the_same_item_comes_back_with_its_capability_in_the_same_place():
    note = next(
        item for item in main_menu({"write", "ask"})[2].items if item.label == "This note"
    )
    assert [i.label for i in note.submenu[0].items] == [
        "New Note…", "Line Up Tables", "Save", "Undo", "Redo", "Rename…", "Move to Trash…",
        "Ask a Question…", "Pin / Unpin Note", "View as Mind Map", "Copy",
    ]


def test_a_capability_that_adds_a_row_to_the_first_level_adds_it_in_its_group():
    groups = main_menu({"commands", "composition"})
    assert [(item.custom, item.label) for item in groups[0].items] == [
        ("commands", ""), ("", "Go to note…"), ("", "Search the vault…"),
    ]
    assert [i.label for i in groups[1].items] == [
        "Appearance…", "Typography…", "Preferences…", "Composition…"
    ]


def test_a_group_left_empty_by_a_missing_capability_goes_with_it():
    only = (Group((Item("Edit", "win.edit", needs="write"),)), Group((Item("Go", "win.go"),)))
    from glossa import menu

    assert menu._keep(only, frozenset(), "") == (only[1],)


def test_a_submenu_left_empty_is_dropped_and_not_shown_as_a_dead_end():
    from glossa import menu

    sub = Item("Edit", submenu=(Group((Item("Save", "win.save", needs="write"),)),))
    assert menu._keep((Group((sub,)),), frozenset(), "") == ()


def test_the_app_name_is_filled_in_and_never_left_as_a_placeholder():
    for group in main_menu(EVERYTHING, app="Reader"):
        for item in group.items:
            assert "{app}" not in item.label


def test_one_action_has_one_label_wherever_it_appears():
    seen: dict[str, str] = {}
    for item in walk(main_menu(EVERYTHING, app="Reader")):
        if item.action and "::" not in item.action:
            assert seen.setdefault(item.action, item.label) == item.label


def test_every_row_is_exactly_one_kind():
    for item in walk(MAIN_MENU):
        kinds = [bool(item.action), bool(item.submenu), bool(item.custom), bool(item.leaf)]
        assert sum(kinds) == 1, item


def test_every_capability_the_table_asks_for_is_documented():
    asked = {item.needs for item in walk(MAIN_MENU) if item.needs}
    assert asked == EVERYTHING
    import glossa.menu

    for name in asked:
        assert f"`{name}`" in glossa.menu.__doc__


def test_the_action_names_drop_their_targets():
    names = action_names(main_menu(set()))
    assert "win.appearance" in names
    assert "win.reader-font" in names
    assert not [name for name in names if "::" in name]


@pytest.mark.parametrize("held", [set(), {"write"}, EVERYTHING])
def test_the_table_is_not_changed_by_asking_for_a_menu(held):
    before = MAIN_MENU
    main_menu(held, app="Reader")
    assert MAIN_MENU == before
