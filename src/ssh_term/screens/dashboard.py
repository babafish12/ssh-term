"""Dashboard screen — main view with connection table."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual import on

from ssh_term import theme
from ssh_term.widgets.connection_table import ConnectionTable
from ssh_term.screens.connection_form import ConnectionFormModal
from ssh_term.screens.confirm_dialog import ConfirmDialog


class ActionBar(Horizontal):
    """Navigable action bar with arrow-key support."""

    DEFAULT_CSS = """
    ActionBar {
        dock: bottom;
        height: 3;
        background: """ + theme.SURFACE + """;
        align: center middle;
        padding: 0 1;
    }
    ActionBar Button {
        margin: 0 1;
        min-width: 16;
    }
    ActionBar Button:focus {
        background: """ + theme.PRIMARY + """;
        color: """ + theme.BG + """;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("Add [a]", id="act-add")
        yield Button("Edit [e]", id="act-edit")
        yield Button("Delete [d]", id="act-delete")
        yield Button("Connect [⏎]", id="act-connect")
        yield Button("Files [f]", id="act-files")
        yield Button("Quit [q]", id="act-quit")

    def on_key(self, event) -> None:
        buttons = list(self.query(Button))
        focused = self.screen.focused
        if focused not in buttons:
            return
        idx = buttons.index(focused)
        if event.key == "left" and idx > 0:
            buttons[idx - 1].focus()
            event.prevent_default()
            event.stop()
        elif event.key == "right" and idx < len(buttons) - 1:
            buttons[idx + 1].focus()
            event.prevent_default()
            event.stop()


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
        Binding("a", "add_connection", "Add", show=False),
        Binding("e", "edit_connection", "Edit", show=False),
        Binding("d", "delete_connection", "Delete", show=False),
        Binding("enter", "connect", "Connect", show=False),
        Binding("f", "file_transfer", "File Transfer", show=False),
        Binding("q", "quit", "Quit", show=False),
        Binding("tab", "toggle_focus", "Switch Focus", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Static("SSH Terminal Manager", id="title-bar")
        with Vertical():
            yield ConnectionTable(id="conn-table")
        yield ActionBar()

    def on_mount(self) -> None:
        self._refresh_table()
        self.query_one("#conn-table", ConnectionTable).focus()

    def action_toggle_focus(self) -> None:
        table = self.query_one("#conn-table", ConnectionTable)
        bar = self.query_one(ActionBar)
        buttons = list(bar.query(Button))
        if self.focused == table:
            buttons[0].focus()
        else:
            table.focus()

    def _refresh_table(self) -> None:
        table = self.query_one("#conn-table", ConnectionTable)
        table.load_connections(self.app.config_manager.connections)

    def _get_selected_id(self) -> str | None:
        table = self.query_one("#conn-table", ConnectionTable)
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return str(row_key)

    # --- Button handlers ---

    @on(Button.Pressed, "#act-add")
    def _btn_add(self) -> None:
        self.action_add_connection()

    @on(Button.Pressed, "#act-edit")
    def _btn_edit(self) -> None:
        self.action_edit_connection()

    @on(Button.Pressed, "#act-delete")
    def _btn_delete(self) -> None:
        self.action_delete_connection()

    @on(Button.Pressed, "#act-connect")
    def _btn_connect(self) -> None:
        self.action_connect()

    @on(Button.Pressed, "#act-files")
    def _btn_files(self) -> None:
        self.action_file_transfer()

    @on(Button.Pressed, "#act-quit")
    def _btn_quit(self) -> None:
        self.action_quit()

    # --- Actions ---

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
