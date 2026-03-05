"""Full-screen SSH terminal."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding

from ssh_term import theme
from ssh_term.models.connection import SSHConnection
from ssh_term.widgets.terminal_emulator import TerminalEmulator


class TerminalScreen(Screen):
    CSS = """
    TerminalScreen {
        background: """ + theme.BG + """;
    }
    TerminalScreen #term-status {
        dock: bottom;
        height: 1;
        background: """ + theme.SURFACE + """;
        color: """ + theme.MUTED + """;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+d", "disconnect", "Disconnect", priority=True),
        Binding("ctrl+f", "file_transfer", "File Transfer", priority=True),
    ]

    def __init__(self, connection: SSHConnection, **kwargs) -> None:
        super().__init__(**kwargs)
        self.connection = connection

    def compose(self) -> ComposeResult:
        channel = self.app.ssh_manager.open_shell(self.connection.id)
        yield TerminalEmulator(channel, id="terminal")
        yield Static(
            f" {self.connection.name} ({self.connection.host})  |  Ctrl+D disconnect  Ctrl+F files",
            id="term-status",
        )

    def on_mount(self) -> None:
        self.query_one("#terminal").focus()

    def on_terminal_emulator_disconnected(self, _event) -> None:
        self.app.ssh_manager.disconnect(self.connection.id)
        self.app.pop_screen()
        self.app.notify("Disconnected")

    def action_disconnect(self) -> None:
        terminal = self.query_one("#terminal", TerminalEmulator)
        terminal.stop()
        self.app.ssh_manager.disconnect(self.connection.id)
        self.app.pop_screen()
        self.app.notify("Disconnected")

    def action_file_transfer(self) -> None:
        from ssh_term.screens.file_transfer import FileTransferScreen
        self.app.push_screen(FileTransferScreen(self.connection))
