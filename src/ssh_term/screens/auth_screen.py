"""Authentication screen — master password setup and login."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Center
from textual import on

class AuthScreen(ModalScreen[bool]):
    CSS = """
    AuthScreen {
        align: center middle;
    }
    AuthScreen #auth-container {
        width: 50;
        height: auto;
        max-height: 22;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    AuthScreen .auth-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    AuthScreen .auth-subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    AuthScreen Input {
        margin-bottom: 1;
    }
    AuthScreen .auth-error {
        color: $error;
        text-align: center;
        margin-bottom: 1;
    }
    AuthScreen Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self, is_first_run: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.is_first_run = is_first_run

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="auth-container"):
                yield Static("SSH Terminal Manager", classes="auth-title")
                if self.is_first_run:
                    yield Static("Set your master password", classes="auth-subtitle")
                    yield Input(placeholder="Password", password=True, id="password")
                    yield Input(placeholder="Confirm password", password=True, id="confirm")
                else:
                    yield Static("Enter your master password", classes="auth-subtitle")
                    yield Input(placeholder="Password", password=True, id="password")
                yield Static("", id="error-msg", classes="auth-error")
                yield Button("Unlock", variant="primary", id="unlock-btn")

    def on_mount(self) -> None:
        self.query_one("#password", Input).focus()

    @on(Button.Pressed, "#unlock-btn")
    def _on_unlock(self) -> None:
        self._try_auth()

    @on(Input.Submitted)
    def _on_submit(self) -> None:
        self._try_auth()

    def _try_auth(self) -> None:
        password = self.query_one("#password", Input).value
        error = self.query_one("#error-msg", Static)

        if not password:
            error.update("Password cannot be empty")
            return

        if self.is_first_run:
            confirm = self.query_one("#confirm", Input).value
            if password != confirm:
                error.update("Passwords do not match")
                return
            self._setup_password(password)
        else:
            self._verify_password(password)

    def _setup_password(self, password: str) -> None:
        app = self.app
        salt = app.auth_manager.generate_salt()
        hashed = app.auth_manager.hash_password(password)
        app.config_manager.master_password_hash = hashed
        app.config_manager.salt_bytes = salt
        app.config_manager.save()
        app.auth_manager.init_fernet(password, salt)
        self.dismiss(True)

    def _verify_password(self, password: str) -> None:
        app = self.app
        hashed = app.config_manager.master_password_hash
        if app.auth_manager.verify_password(password, hashed):
            salt = app.config_manager.salt_bytes
            app.auth_manager.init_fernet(password, salt)
            self.dismiss(True)
        else:
            error = self.query_one("#error-msg", Static)
            error.update("Wrong password")
