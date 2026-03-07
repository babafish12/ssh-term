"""Styled DataTable for SSH connections."""

from __future__ import annotations

from textual.widgets import DataTable

from ssh_term.models.connection import SSHConnection
from ssh_term import theme


class ConnectionTable(DataTable):
    DEFAULT_CSS = """
    ConnectionTable {
        height: 1fr;
    }
    """

    can_focus = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.show_cursor = True

    def on_mount(self) -> None:
        self.add_columns("Name", "IP", "User", "Port", "Auth", "Tags", "Last Connected")

    def load_connections(self, connections: list[SSHConnection]) -> None:
        self.clear()
        for conn in connections:
            tags = ", ".join(conn.tags) if conn.tags else ""
            last = conn.last_connected[:10] if conn.last_connected else "never"
            self.add_row(
                conn.name,
                conn.host,
                conn.username,
                str(conn.port),
                conn.auth_method,
                tags,
                last,
                key=conn.id,
            )
