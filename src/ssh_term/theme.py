"""Theme presets for SSH Terminal Manager."""

from __future__ import annotations

from textual.theme import Theme

THEMES: list[Theme] = [
    Theme(
        name="tokyo-night",
        primary="#7aa2f7",
        secondary="#9ece6a",
        accent="#bb9af7",
        warning="#e0af68",
        error="#f7768e",
        success="#9ece6a",
        foreground="#c0caf5",
        background="#1a1b26",
        surface="#24283b",
        panel="#414868",
        dark=True,
        variables={"highlight": "#292e42", "info": "#7dcfff"},
    ),
    Theme(
        name="catppuccin-mocha",
        primary="#89b4fa",
        secondary="#a6e3a1",
        accent="#cba6f7",
        warning="#f9e2af",
        error="#f38ba8",
        success="#a6e3a1",
        foreground="#cdd6f4",
        background="#1e1e2e",
        surface="#313244",
        panel="#45475a",
        dark=True,
        variables={"highlight": "#313244", "info": "#89dceb"},
    ),
    Theme(
        name="dracula",
        primary="#bd93f9",
        secondary="#50fa7b",
        accent="#ff79c6",
        warning="#f1fa8c",
        error="#ff5555",
        success="#50fa7b",
        foreground="#f8f8f2",
        background="#282a36",
        surface="#44475a",
        panel="#6272a4",
        dark=True,
        variables={"highlight": "#44475a", "info": "#8be9fd"},
    ),
    Theme(
        name="nord",
        primary="#88c0d0",
        secondary="#a3be8c",
        accent="#b48ead",
        warning="#ebcb8b",
        error="#bf616a",
        success="#a3be8c",
        foreground="#eceff4",
        background="#2e3440",
        surface="#3b4252",
        panel="#4c566a",
        dark=True,
        variables={"highlight": "#3b4252", "info": "#81a1c1"},
    ),
    Theme(
        name="gruvbox-dark",
        primary="#83a598",
        secondary="#b8bb26",
        accent="#d3869b",
        warning="#fabd2f",
        error="#fb4934",
        success="#b8bb26",
        foreground="#ebdbb2",
        background="#282828",
        surface="#3c3836",
        panel="#504945",
        dark=True,
        variables={"highlight": "#3c3836", "info": "#83a598"},
    ),
    Theme(
        name="one-dark",
        primary="#61afef",
        secondary="#98c379",
        accent="#c678dd",
        warning="#e5c07b",
        error="#e06c75",
        success="#98c379",
        foreground="#abb2bf",
        background="#282c34",
        surface="#3e4451",
        panel="#4b5263",
        dark=True,
        variables={"highlight": "#3e4451", "info": "#56b6c2"},
    ),
]

THEME_NAMES: list[str] = [t.name for t in THEMES]

# ANSI color maps per theme (for terminal emulator)
ANSI_COLORS: dict[str, dict[int, str]] = {
    "tokyo-night": {
        0: "#15161e", 1: "#f7768e", 2: "#9ece6a", 3: "#e0af68",
        4: "#7aa2f7", 5: "#bb9af7", 6: "#7dcfff", 7: "#a9b1d6",
        8: "#414868", 9: "#f7768e", 10: "#9ece6a", 11: "#e0af68",
        12: "#7aa2f7", 13: "#bb9af7", 14: "#7dcfff", 15: "#c0caf5",
    },
    "catppuccin-mocha": {
        0: "#45475a", 1: "#f38ba8", 2: "#a6e3a1", 3: "#f9e2af",
        4: "#89b4fa", 5: "#cba6f7", 6: "#89dceb", 7: "#bac2de",
        8: "#585b70", 9: "#f38ba8", 10: "#a6e3a1", 11: "#f9e2af",
        12: "#89b4fa", 13: "#cba6f7", 14: "#89dceb", 15: "#cdd6f4",
    },
    "dracula": {
        0: "#21222c", 1: "#ff5555", 2: "#50fa7b", 3: "#f1fa8c",
        4: "#bd93f9", 5: "#ff79c6", 6: "#8be9fd", 7: "#f8f8f2",
        8: "#6272a4", 9: "#ff6e6e", 10: "#69ff94", 11: "#ffffa5",
        12: "#d6acff", 13: "#ff92df", 14: "#a4ffff", 15: "#ffffff",
    },
    "nord": {
        0: "#3b4252", 1: "#bf616a", 2: "#a3be8c", 3: "#ebcb8b",
        4: "#81a1c1", 5: "#b48ead", 6: "#88c0d0", 7: "#e5e9f0",
        8: "#4c566a", 9: "#bf616a", 10: "#a3be8c", 11: "#ebcb8b",
        12: "#81a1c1", 13: "#b48ead", 14: "#8fbcbb", 15: "#eceff4",
    },
    "gruvbox-dark": {
        0: "#282828", 1: "#cc241d", 2: "#98971a", 3: "#d79921",
        4: "#458588", 5: "#b16286", 6: "#689d6a", 7: "#a89984",
        8: "#928374", 9: "#fb4934", 10: "#b8bb26", 11: "#fabd2f",
        12: "#83a598", 13: "#d3869b", 14: "#8ec07c", 15: "#ebdbb2",
    },
    "one-dark": {
        0: "#282c34", 1: "#e06c75", 2: "#98c379", 3: "#e5c07b",
        4: "#61afef", 5: "#c678dd", 6: "#56b6c2", 7: "#abb2bf",
        8: "#5c6370", 9: "#e06c75", 10: "#98c379", 11: "#e5c07b",
        12: "#61afef", 13: "#c678dd", 14: "#56b6c2", 15: "#ffffff",
    },
}


# Fixed terminal colors — always Tokyo Night regardless of UI theme
TERMINAL_FG = "#c0caf5"
TERMINAL_BG = "#1a1b26"
TERMINAL_ANSI = ANSI_COLORS["tokyo-night"]


def get_color(theme_name: str, color_name: str) -> str:
    """Get a hex color value from a registered theme by name."""
    for t in THEMES:
        if t.name == theme_name:
            val = getattr(t, color_name, None)
            if val is not None:
                return str(val)
            return t.variables.get(color_name, "#c0caf5")
    return "#c0caf5"


def get_ansi_colors(theme_name: str) -> dict[int, str]:
    return ANSI_COLORS.get(theme_name, ANSI_COLORS["tokyo-night"])


def next_theme(current: str) -> str:
    idx = THEME_NAMES.index(current) if current in THEME_NAMES else -1
    return THEME_NAMES[(idx + 1) % len(THEME_NAMES)]
