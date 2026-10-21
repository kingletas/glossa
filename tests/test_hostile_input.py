"""A note is hostile input: a few hundred bytes of it must not cost gigabytes, and
whatever it trips inside a renderer reaches the caller as that renderer's one error."""

import pytest

from glossa import excalidraw, mermaid
from glossa.bases import _sort_key, render_base
from glossa.dataview import DataviewEngine, Evaluator, Row
from glossa.dql import DqlError, parse_expression
from glossa.lzstring import TooLarge, decompress_base64

_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="


def compress_base64(text: str) -> str:
    """lz-string's compressToBase64, so the tests can build a payload of any size."""
    dictionary, to_create = {}, set()
    w, enlarge_in, size, num_bits = "", 2, 3, 2
    out, value_bits, position = [], 0, 0

    def put(value: int, count: int) -> None:
        nonlocal value_bits, position
        for _ in range(count):
            value_bits = (value_bits << 1) | (value & 1)
            if position == 5:
                position = 0
                out.append(_KEY[value_bits])
                value_bits = 0
            else:
                position += 1
            value >>= 1

    def emit(word: str) -> None:
        nonlocal enlarge_in, num_bits
        if word in to_create:
            if ord(word[0]) < 256:
                put(0, num_bits)
                put(ord(word[0]), 8)
            else:
                put(1, num_bits)
                put(ord(word[0]), 16)
            enlarge_in -= 1
            if enlarge_in == 0:
                enlarge_in, num_bits = 1 << num_bits, num_bits + 1
            to_create.discard(word)
        else:
            put(dictionary[word], num_bits)
        enlarge_in -= 1
        if enlarge_in == 0:
            enlarge_in, num_bits = 1 << num_bits, num_bits + 1

    for character in text:
        if character not in dictionary:
            dictionary[character] = size
            size += 1
            to_create.add(character)
        if w + character in dictionary:
            w += character
            continue
        emit(w)
        dictionary[w + character] = size
        size += 1
        w = character
    if w:
        emit(w)
    put(2, num_bits)
    while True:
        value_bits <<= 1
        if position == 5:
            out.append(_KEY[value_bits])
            break
        position += 1
    encoded = "".join(out)
    return encoded + "=" * (-len(encoded) % 4)


def test_the_test_compressor_round_trips():
    for text in ("", "a", "hello world", "abababababab", "é ü 漢字"):
        assert decompress_base64(compress_base64(text)) == text


def test_a_decompression_bomb_stops_at_the_limit():
    payload = compress_base64("a" * 200_000)
    assert len(payload) < 2_000
    with pytest.raises(TooLarge):
        decompress_base64(payload, limit=10_000)
    assert decompress_base64(payload) == "a" * 200_000


def test_a_drawing_that_decompresses_past_the_cap_is_refused(monkeypatch):
    monkeypatch.setattr(excalidraw, "MAX_DRAWING_BYTES", 10_000)
    note = f"```compressed-json\n{compress_base64('a' * 200_000)}\n```\n"
    assert "too large" in excalidraw.excalidraw_body(note)


def test_a_base_with_yaml_aliases_is_refused_before_they_expand():
    bomb = "a: &a [x,x,x,x,x,x,x,x,x]\n"
    for index in range(1, 8):
        previous = "a" if index == 1 else f"a{index - 1}"
        bomb += f"a{index}: &a{index} [" + ",".join([f"*{previous}"] * 9) + "]\n"
    bomb += "views:\n  - type: table\n    name: *a7\n"
    assert "aliases" in render_base(None, bomb)


def test_a_value_that_grows_past_the_ceiling_is_refused():
    expression = '"a"'
    for _ in range(8):
        expression = f'replace({expression}, "a", "aaaaaaaaaa")'
    with pytest.raises(DqlError, match="grew past"):
        Evaluator(Row({}, {})).evaluate(parse_expression(expression), Row({}, {}))


class Graph:
    """The smallest graph the engine reads: one note, no links, no tags."""

    props = {"a.md": {}}
    outgoing: dict = {}
    backlinks: dict = {}
    note_tags: dict = {}
    tasks: dict = {}
    meta = {"a.md": (0.0, 0)}

    def notes_tagged(self, tag):
        return []


TRIPS = ["lower()", 'round("abc")', "sum(5)", "(" * 2000 + "1" + ")" * 2000]


@pytest.mark.parametrize("expression", TRIPS)
def test_what_an_expression_trips_reaches_the_caller_as_a_dql_error(expression):
    with pytest.raises(DqlError):
        DataviewEngine(Graph()).run_inline(expression, "a.md")


def test_mermaid_raises_only_its_own_error():
    with pytest.raises(mermaid.MermaidError):
        mermaid.render_mermaid('pie\n"a" : 1.2.3\n')


def test_a_fan_out_past_the_edge_cap_is_refused():
    sources = " & ".join(f"s{n}" for n in range(50))
    targets = " & ".join(f"t{n}" for n in range(50))
    with pytest.raises(mermaid.MermaidError, match="edges"):
        mermaid.render_mermaid(f"graph TD\n{sources} --> {targets}\n")


def test_base_rows_sort_numbers_by_value():
    assert sorted([10, "b", 2, None, 9, "A"], key=_sort_key) == [2, 9, 10, "A", "b", None]
