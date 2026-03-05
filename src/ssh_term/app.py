"""Main Textual application."""

from __future__ import annotations

from textual.app import App

from ssh_term.models.auth import AuthManager
from ssh_term.models.config import ConfigManager
from ssh_term.services.ssh_manager import SSHManager
from ssh_term.screens.auth_screen import AuthScreen
from ssh_term.screens.dashboard import DashboardScreen
from ssh_term import theme


class SSHTermApp(App):
    CSS = """
    Screen {
        background: """ + theme.BG + """;
        color: """ + theme.FG + """;
    }
    DataTable {
        background: """ + theme.BG + """;
        color: """ + theme.FG + """;
    }
    DataTable > .datatable--header {
        background: """ + theme.SURFACE + """;
        color: """ + theme.PRIMARY + """;
        text-style: bold;
    }
    DataTable > .datatable--cursor {
        background: """ + theme.BG_HIGHLIGHT + """;
        color: """ + theme.FG + """;
    }
    DataTable > .datatable--even-row {
        background: """ + theme.BG + """;
    }
    DataTable > .datatable--odd-row {
        background: """ + theme.SURFACE + """;
    }
    Input {
        background: """ + theme.BG_HIGHLIGHT + """;
        color: """ + theme.FG + """;
        border: tall """ + theme.BORDER + """;
    }
    Input:focus {
        border: tall """ + theme.PRIMARY + """;
    }
    Button {
        background: """ + theme.SURFACE + """;
        color: """ + theme.FG + """;
        border: tall """ + theme.BORDER + """;
    }
    Button:hover {
        background: """ + theme.BG_HIGHLIGHT + """;
    }
    Button.-primary {
        background: """ + theme.PRIMARY + """;
        color: """ + theme.BG + """;
    }
    Button.-error {
        background: """ + theme.ERROR + """;
        color: """ + theme.BG + """;
    }
    Select {
        background: """ + theme.BG_HIGHLIGHT + """;
        color: """ + theme.FG + """;
        border: tall """ + theme.BORDER + """;
    }
    ProgressBar Bar {
        color: """ + theme.PRIMARY + """;
        background: """ + theme.SURFACE + """;
    }
    Tree {
        background: """ + theme.BG + """;
        color: """ + theme.FG + """;
    }
    Tree > .tree--cursor {
        background: """ + theme.BG_HIGHLIGHT + """;
        color: """ + theme.FG + """;
    }
    DirectoryTree {
        background: """ + theme.BG + """;
        color: """ + theme.FG + """;
    }
    Toast {
        background: """ + theme.SURFACE + """;
        color: """ + theme.FG + """;
    }
    """

    TITLE = "SSH Terminal Manager"

    def __init__(self) -> None:
        super().__init__()
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager()
        self.ssh_manager = SSHManager()

    def on_mount(self) -> None:
        self.config_manager.load()

        def on_auth(result: bool) -> None:
            if result:
                self.push_screen(DashboardScreen())
            else:
                self.exit()

        self.push_screen(
            AuthScreen(is_first_run=self.config_manager.is_first_run),
            callback=on_auth,
        )

    def on_unmount(self) -> None:
        self.ssh_manager.disconnect_all()
