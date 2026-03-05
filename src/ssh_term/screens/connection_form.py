"""Add/Edit connection modal form."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button, Select
from textual.containers import Vertical, Horizontal, Center
from textual import on

from ssh_term import theme
from ssh_term.models.connection import SSHConnection


class ConnectionFormModal(ModalScreen[SSHConnection | None]):
    CSS = """
    ConnectionFormModal {
        align: center middle;
    }
    ConnectionFormModal #form-container {
        width: 60;
        height: auto;
        max-height: 35;
        border: thick $primary;
        background: """ + theme.SURFACE + """;
        padding: 1 2;
        overflow-y: auto;
    }
    ConnectionFormModal .form-title {
        text-align: center;
        text-style: bold;
        color: """ + theme.PRIMARY + """;
        margin-bottom: 1;
    }
    ConnectionFormModal .form-label {
        margin-top: 1;
        color: """ + theme.FG_DIM + """;
    }
    ConnectionFormModal Input {
        margin-bottom: 0;
    }
    ConnectionFormModal Select {
        margin-bottom: 0;
    }
    ConnectionFormModal .form-error {
        color: """ + theme.ERROR + """;
        text-align: center;
        margin-top: 1;
    }
    ConnectionFormModal Horizontal {
        height: 3;
        align: center middle;
        margin-top: 1;
    }
    ConnectionFormModal Horizontal Button {
        margin: 0 1;
    }
    """

    def __init__(self, connection: SSHConnection | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.connection = connection

    def compose(self) -> ComposeResult:
        c = self.connection
        title = "Edit Connection" if c else "Add Connection"

        with Center():
            with Vertical(id="form-container"):
                yield Static(title, classes="form-title")
                yield Static("Name", classes="form-label")
                yield Input(value=c.name if c else "", placeholder="e.g. Prod Server", id="name")
                yield Static("Host", classes="form-label")
                yield Input(value=c.host if c else "", placeholder="e.g. web01.example.com", id="host")
                yield Static("IP (optional)", classes="form-label")
                yield Input(value=c.ip if c else "", placeholder="e.g. 192.168.1.50", id="ip")
                yield Static("Port", classes="form-label")
                yield Input(value=str(c.port) if c else "22", placeholder="22", id="port")
                yield Static("Username", classes="form-label")
                yield Input(value=c.username if c else "", placeholder="e.g. deploy", id="username")
                yield Static("Auth Method", classes="form-label")
                yield Select(
                    [("SSH Key", "key"), ("Password", "password"), ("SSH Agent", "agent")],
                    value=c.auth_method if c else "key",
                    id="auth_method",
                )
                yield Static("Private Key Path", classes="form-label")
                yield Input(
                    value=c.private_key_path if c else "~/.ssh/id_ed25519",
                    placeholder="~/.ssh/id_ed25519",
                    id="key_path",
                )
                yield Static("Password (for password auth)", classes="form-label")
                yield Input(value="", password=True, placeholder="SSH password", id="password")
                yield Static("Tags (comma-separated)", classes="form-label")
                yield Input(
                    value=", ".join(c.tags) if c and c.tags else "",
                    placeholder="e.g. prod, web",
                    id="tags",
                )
                yield Static("", id="form-error", classes="form-error")
                with Horizontal():
                    yield Button("Cancel", variant="default", id="cancel-btn")
                    yield Button("Save", variant="primary", id="save-btn")

    def on_mount(self) -> None:
        self.query_one("#name", Input).focus()

    @on(Button.Pressed, "#cancel-btn")
    def _cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#save-btn")
    def _save(self) -> None:
        self._do_save()

    def _do_save(self) -> None:
        name = self.query_one("#name", Input).value.strip()
        host = self.query_one("#host", Input).value.strip()
        username = self.query_one("#username", Input).value.strip()
        port_str = self.query_one("#port", Input).value.strip()
        error = self.query_one("#form-error", Static)

        if not name:
            error.update("Name is required")
            return
        if not host:
            error.update("Host is required")
            return
        if not username:
            error.update("Username is required")
            return
        try:
            port = int(port_str)
        except ValueError:
            error.update("Port must be a number")
            return

        auth_method = self.query_one("#auth_method", Select).value
        key_path = self.query_one("#key_path", Input).value.strip()
        password = self.query_one("#password", Input).value
        ip = self.query_one("#ip", Input).value.strip()
        tags_raw = self.query_one("#tags", Input).value.strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

        encrypted_pw = ""
        if auth_method == "password" and password:
            try:
                encrypted_pw = self.app.auth_manager.encrypt(password)
            except Exception:
                error.update("Encryption error")
                return

        if self.connection:
            conn = self.connection
            conn.name = name
            conn.host = host
            conn.ip = ip
            conn.port = port
            conn.username = username
            conn.auth_method = auth_method
            conn.private_key_path = key_path
            conn.tags = tags
            if encrypted_pw:
                conn.password_encrypted = encrypted_pw
        else:
            conn = SSHConnection(
                name=name,
                host=host,
                ip=ip,
                port=port,
                username=username,
                auth_method=auth_method,
                private_key_path=key_path,
                password_encrypted=encrypted_pw,
                tags=tags,
            )

        self.dismiss(conn)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
