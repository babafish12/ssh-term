"""Dashboard screen — main view with connection table."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, DataTable
from textual.binding import Binding

from ssh_term import theme
from ssh_term.widgets.connection_table import ConnectionTable
from ssh_term.screens.connection_form import ConnectionFormModal
from ssh_term.screens.confirm_dialog import ConfirmDialog


class HintBar(Static):
    """Compact keybinding hint bar."""

    DEFAULT_CSS = """
    HintBar {
        dock: bottom;
        height: 1;
        background: """ + theme.SURFACE + """;
        color: """ + theme.MUTED + """;
        padding: 0 1;
    }
    """

    def __init__(self) -> None:
        hints = (
            "[bold " + theme.PRIMARY + "]a[/] Add  "
            "[bold " + theme.PRIMARY + "]e[/] Edit  "
            "[bold " + theme.PRIMARY + "]d[/] Delete  "
            "[bold " + theme.PRIMARY + "]\u23ce[/] Connect  "
            "[bold " + theme.PRIMARY + "]f[/] Files  "
            "[bold " + theme.PRIMARY + "]q[/] Quit"
        )
        super().__init__(hints)


class DashboardScreen(Screen):
    CSS = """
    DashboardScreen {
        background: """ + theme.BG + """;
    }
    DashboardScreen #title-bar {
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: """ + theme.PRIMARY + """;
        background: """ + theme.SURFACE + """;
        border-bottom: solid """ + theme.BORDER + """;
    }
    DashboardScreen #conn-table {
        margin: 1 2;
    }
    """

    BINDINGS = [
        Binding("a", "add_connection", "Add", show=False, priority=True),
        Binding("e", "edit_connection", "Edit", show=False, priority=True),
        Binding("d", "delete_connection", "Delete", show=False, priority=True),
        Binding("enter", "connect", "Connect", show=False, priority=True),
        Binding("f", "file_transfer", "File Transfer", show=False, priority=True),
        Binding("q", "quit", "Quit", show=False, priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static("SSH Terminal Manager", id="title-bar")
        yield ConnectionTable(id="conn-table")
        yield HintBar()

    def on_mount(self) -> None:
        self._refresh_table()
        self.query_one("#conn-table", ConnectionTable).focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.action_connect()

    def _refresh_table(self) -> None:
        table = self.query_one("#conn-table", ConnectionTable)
        table.load_connections(self.app.config_manager.connections)

    def _get_selected_id(self) -> str | None:
        table = self.query_one("#conn-table", ConnectionTable)
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return row_key.value

    def action_add_connection(self) -> None:
        def on_result(conn) -> None:
            if conn:
                self.app.config_manager.add_connection(conn)
                self._refresh_table()
                self.notify(f"Added {conn.name}")

        self.app.push_screen(ConnectionFormModal(), callback=on_result)

    def action_edit_connection(self) -> None:
        conn_id = self._get_selected_id()
        if not conn_id:
            self.notify("No connection selected", severity="warning")
            return
        conn = self.app.config_manager.get_connection(conn_id)
        if not conn:
            self.notify("Connection not found", severity="error")
            return

        def on_result(updated) -> None:
            if updated:
                self.app.config_manager.update_connection(updated)
                self._refresh_table()
                self.notify(f"Updated {updated.name}")

        self.app.push_screen(ConnectionFormModal(connection=conn), callback=on_result)

    def action_delete_connection(self) -> None:
        conn_id = self._get_selected_id()
        if not conn_id:
            self.notify("No connection selected", severity="warning")
            return
        conn = self.app.config_manager.get_connection(conn_id)
        if not conn:
            self.notify("Connection not found", severity="error")
            return

        def on_confirm(confirmed: bool) -> None:
            if confirmed:
                self.app.config_manager.delete_connection(conn_id)
                self._refresh_table()
                self.notify(f"Deleted {conn.name}")

        self.app.push_screen(
            ConfirmDialog("Delete Connection", f"Delete '{conn.name}'?"),
            callback=on_confirm,
        )

    def action_connect(self) -> None:
        conn_id = self._get_selected_id()
        if not conn_id:
            self.notify("No connection selected", severity="warning")
            return
        conn = self.app.config_manager.get_connection(conn_id)
        if not conn:
            self.notify("Connection not found", severity="error")
            return

        password = None
        if conn.auth_method == "password" and conn.password_encrypted:
            try:
                password = self.app.auth_manager.decrypt(conn.password_encrypted)
            except Exception:
                self.notify("Failed to decrypt password", severity="error")
                return

        try:
            self.app.ssh_manager.connect(conn, password=password)
            conn.touch()
            self.app.config_manager.update_connection(conn)
            self._refresh_table()
        except Exception as e:
            self.notify(f"Connection failed: {e}", severity="error")
            return

        from ssh_term.screens.terminal_screen import TerminalScreen
        self.app.push_screen(TerminalScreen(conn))

    def action_file_transfer(self) -> None:
        conn_id = self._get_selected_id()
        if not conn_id:
            self.notify("No connection selected", severity="warning")
            return
        conn = self.app.config_manager.get_connection(conn_id)
        if not conn:
            self.notify("Connection not found", severity="error")
            return

        if not self.app.ssh_manager.is_connected(conn.id):
            password = None
            if conn.auth_method == "password" and conn.password_encrypted:
                try:
                    password = self.app.auth_manager.decrypt(conn.password_encrypted)
                except Exception:
                    self.notify("Failed to decrypt password", severity="error")
                    return
            try:
                self.app.ssh_manager.connect(conn, password=password)
            except Exception as e:
                self.notify(f"Connection failed: {e}", severity="error")
                return

        from ssh_term.screens.file_transfer import FileTransferScreen
        self.app.push_screen(FileTransferScreen(conn))

    def action_quit(self) -> None:
        self.app.exit()
