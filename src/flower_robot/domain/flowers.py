from __future__ import annotations


FLOWER_COLORS: dict[str, tuple[str, ...]] = {
    "rose": ("red", "pink", "white", "yellow", "burgundy"),
    "tulip": ("red", "yellow", "purple", "orange", "green", "mauve", "magenta"),
    "orchid": ("purple", "white", "pink", "fuchsia"),
    "juliet_rose": ("gold", "light_pink", "yellow"),
}


FLOWER_LABELS: dict[str, str] = {
    "rose": "Rose",
    "tulip": "Tulip",
    "orchid": "Orchid",
    "juliet_rose": "Juliet Rose",
}


COLOR_LABELS: dict[str, str] = {
    "red": "red",
    "pink": "pink",
    "white": "white",
    "yellow": "yellow",
    "burgundy": "burgundy",
    "purple": "purple",
    "orange": "orange",
    "green": "green",
    "mauve": "mauve",
    "magenta": "magenta",
    "fuchsia": "fuchsia",
    "gold": "gold",
    "light_pink": "light pink",
}


def flower_label(flower_type: str) -> str:
    return FLOWER_LABELS.get(flower_type, flower_type.replace("_", " ").title())


def color_label(color: str) -> str:
    return COLOR_LABELS.get(color, color.replace("_", " "))
