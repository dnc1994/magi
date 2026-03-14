from magi.themes import THEMES, Theme, get_next_theme


def test_theme_fields():
    t = THEMES[0]
    for field in ("name", "primary", "accent", "background", "border", "dim", "scanlines"):
        assert hasattr(t, field)


def test_three_themes_exist():
    assert len(THEMES) == 3
    names = [t.name for t in THEMES]
    assert "AMBER" in names
    assert "BLUE" in names
    assert "RED ALERT" in names


def test_get_next_theme_cycles():
    amber, blue, red = THEMES[0], THEMES[1], THEMES[2]
    assert get_next_theme(amber) is blue
    assert get_next_theme(blue) is red
    assert get_next_theme(red) is amber


def test_colors_are_hex():
    for theme in THEMES:
        for color in (theme.primary, theme.accent, theme.background, theme.border, theme.dim):
            assert color.startswith("#") and len(color) == 7, f"Bad hex: {color!r}"


def test_amber_has_scanlines():
    amber = next(t for t in THEMES if t.name == "AMBER")
    assert amber.scanlines is True


def test_others_no_scanlines():
    for t in THEMES:
        if t.name != "AMBER":
            assert t.scanlines is False
