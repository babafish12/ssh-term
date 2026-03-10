"""Main Textual application."""

from __future__ import annotations

from textual.app import App

from ssh_term.models.auth import AuthManager
from ssh_term.models.config import ConfigManager
from ssh_term.services.ssh_manager import SSHManager
from ssh_term.screens.auth_screen import AuthScreen
from ssh_term.screens.dashboard import DashboardScreen
from ssh_term.theme import THEMES


class SSHTermApp(App):
    CSS = """
    Screen {
        background: $background;
        color: $foreground;
    }
    DataTable {
        background: $background;
        color: $foreground;
    }
    DataTable > .datatable--header {
        background: $surface;
        color: $primary;
        text-style: bold;
    }
    DataTable > .datatable--cursor {
        background: $panel;
        color: $foreground;
    }
    DataTable > .datatable--even-row {
        background: $background;
    }
    DataTable > .datatable--odd-row {
        background: $surface;
    }
    Input {
        background: $panel;
        color: $foreground;
        border: tall $panel;
    }
    Input:focus {
        border: tall $primary;
    }
    Button {
        background: $surface;
        color: $foreground;
        border: tall $panel;
    }
    Button:hover {
        background: $panel;
    }
    Button.-primary {
        background: $primary;
        color: $background;
    }
    Button.-error {
        background: $error;
        color: $background;
    }
    Select {
        background: $panel;
        color: $foreground;
        border: tall $panel;
    }
    ProgressBar Bar {
        color: $primary;
        background: $surface;
    }
    Tree {
        background: $background;
        color: $foreground;
    }
    Tree > .tree--cursor {
        background: $primary;
        color: $background;
        text-style: bold;
    }
    Tree:focus > .tree--cursor {
        background: $primary;
        color: $background;
        text-style: bold;
    }
    DirectoryTree {
        background: $background;
        color: $foreground;
    }
    DirectoryTree > .tree--cursor {
        background: $primary;
        color: $background;
        text-style: bold;
    }
    DirectoryTree:focus > .tree--cursor {
        background: $primary;
        color: $background;
        text-style: bold;
    }
    Toast {
        background: $surface;
        color: $foreground;
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

        for t in THEMES:
            self.register_theme(t)
        self.theme = self.config_manager.theme

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
