"""File transfer progress bar widget."""

from __future__ import annotations

from textual.widgets import Static, ProgressBar
from textual.containers import Horizontal


class TransferProgress(Static):
    DEFAULT_CSS = """
    TransferProgress {
        height: 3;
        dock: bottom;
        padding: 0 1;
    }
    TransferProgress Horizontal {
        height: 1;
    }
    TransferProgress .transfer-label {
        width: auto;
        min-width: 20;
    }
    TransferProgress ProgressBar {
        width: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._filename = ""
        self._total = 0

    def compose(self):
        with Horizontal():
            yield Static("", id="transfer-label", classes="transfer-label")
            yield ProgressBar(total=100, show_eta=True, id="transfer-bar")

    def start(self, filename: str, total_bytes: int) -> None:
        self._filename = filename
        self._total = total_bytes
        label = self.query_one("#transfer-label", Static)
        label.update(f"  {filename}")
        bar = self.query_one("#transfer-bar", ProgressBar)
        bar.update(total=100, progress=0)
        self.display = True

    def update_progress(self, transferred: int, total: int) -> None:
        if total > 0:
            pct = (transferred / total) * 100
            bar = self.query_one("#transfer-bar", ProgressBar)
            bar.update(progress=pct)

    def finish(self) -> None:
        bar = self.query_one("#transfer-bar", ProgressBar)
        bar.update(progress=100)
        label = self.query_one("#transfer-label", Static)
        label.update(f"  {self._filename} — done")
