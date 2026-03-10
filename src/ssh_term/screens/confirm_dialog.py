"""Delete confirmation dialog."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal, Center
from textual import on


class ConfirmDialog(ModalScreen[bool]):
    CSS = """
    ConfirmDialog {
        align: center middle;
    }
    ConfirmDialog #confirm-container {
        width: 45;
        height: auto;
        border: thick $error;
        background: $surface;
        padding: 1 2;
    }
    ConfirmDialog .confirm-title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }
    ConfirmDialog .confirm-msg {
        text-align: center;
        color: $foreground;
        margin-bottom: 1;
    }
    ConfirmDialog Horizontal {
        height: 3;
        align: center middle;
    }
    ConfirmDialog Button {
        margin: 0 1;
    }
    """

    def __init__(self, title: str, message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._message = message

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="confirm-container"):
                yield Static(self._title, classes="confirm-title")
                yield Static(self._message, classes="confirm-msg")
                with Horizontal():
                    yield Button("Cancel", variant="default", id="cancel-btn")
                    yield Button("Delete", variant="error", id="delete-btn")

    @on(Button.Pressed, "#cancel-btn")
    def _cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#delete-btn")
    def _confirm(self) -> None:
        self.dismiss(True)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)
