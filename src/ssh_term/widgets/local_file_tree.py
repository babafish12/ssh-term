"""Local directory tree without emoji icons."""

from __future__ import annotations

from textual.widgets import DirectoryTree


class LocalFileTree(DirectoryTree):
    ICON_NODE = "▶ "
    ICON_NODE_EXPANDED = "▼ "
    ICON_FILE = "  "
