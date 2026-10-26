"""The palettes lift a quiet colour until it reads, on every ground it is given."""

from glossa.palettes import PALETTES, STONE_DARK, STONE_LIGHT, channels, contrast_ratio, mix

EVERY_PALETTE = (STONE_LIGHT, STONE_DARK, *PALETTES)


def test_channels_reads_a_colour_as_red_green_and_blue():
    assert channels("#1a2b3c") == (0x1A, 0x2B, 0x3C)


def test_a_colour_lifted_against_several_grounds_clears_every_one_of_them():
    for palette in EVERY_PALETTE:
        grounds = (palette.bg, palette.void, palette.card)
        lifted = palette.legible(palette.muted, grounds)
        for ground in grounds:
            assert contrast_ratio(lifted, ground) >= 4.5, palette.key


def test_one_ground_still_works_as_it_did():
    for palette in EVERY_PALETTE:
        assert palette.legible(palette.muted, palette.bg) == palette.legible(
            palette.muted, (palette.bg,)
        )


def test_the_card_sits_between_the_canvas_and_the_surface():
    for palette in EVERY_PALETTE:
        assert palette.card == mix(palette.bg, palette.surface, 0.6)


def test_the_quiet_labels_clear_the_floor_on_the_canvas_the_rail_and_a_card():
    for palette in EVERY_PALETTE:
        for name, ground in (
            ("canvas", palette.bg),
            ("rail", palette.void),
            ("card", palette.card),
        ):
            ratio = contrast_ratio(palette.chrome_muted, ground)
            assert ratio >= 4.5, f"{palette.key} quiet labels are {ratio:.2f} on the {name}"


def test_a_quiet_colour_that_already_reads_is_left_as_the_theme_states_it():
    assert STONE_DARK.chrome_muted == STONE_DARK.muted
    assert STONE_LIGHT.chrome_muted != STONE_LIGHT.muted
