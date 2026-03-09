"""Dual-pane SFTP file browser screen."""

from __future__ import annotations

import os
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, DirectoryTree, Tree
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual import work

from ssh_term import theme
from ssh_term.models.connection import SSHConnection
from ssh_term.services.sftp_manager import SFTPManager
from ssh_term.widgets.remote_file_tree import RemoteFileTree
from ssh_term.widgets.transfer_progress import TransferProgress


class FileTransferScreen(Screen):
    CSS = """
    FileTransferScreen {
        background: """ + theme.BG + """;
    }
    FileTransferScreen #ft-title {
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: """ + theme.ACCENT + """;
        background: """ + theme.SURFACE + """;
        border-bottom: solid """ + theme.BORDER + """;
    }
    FileTransferScreen #panes {
        height: 1fr;
    }
    FileTransferScreen .pane {
        width: 1fr;
        border: solid """ + theme.BORDER + """;
        margin: 0 1;
    }
    FileTransferScreen .pane-header {
        height: 1;
        text-style: bold;
        padding: 0 1;
        background: """ + theme.BG_HIGHLIGHT + """;
    }
    FileTransferScreen .local-header {
        color: """ + theme.SECONDARY + """;
    }
    FileTransferScreen .remote-header {
        color: """ + theme.CYAN + """;
    }
    FileTransferScreen #ft-status {
        dock: bottom;
        height: 1;
        background: """ + theme.SURFACE + """;
        color: """ + theme.MUTED + """;
        padding: 0 1;
    }
    FileTransferScreen DirectoryTree {
        height: 1fr;
    }
    FileTransferScreen RemoteFileTree {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("c", "copy_file", "Copy"),
        Binding("tab", "switch_pane", "Switch Pane"),
    ]

    def __init__(self, connection: SSHConnection, **kwargs) -> None:
        super().__init__(**kwargs)
        self.connection = connection
        self._sftp_manager: SFTPManager | None = None
        self._active_pane = "local"

    def compose(self) -> ComposeResult:
        yield Static(f"File Transfer — {self.connection.name}", id="ft-title")
        with Horizontal(id="panes"):
            with Vertical(classes="pane"):
                yield Static("Local", classes="pane-header local-header")
                yield DirectoryTree(str(Path.home()), id="local-tree")
            with Vertical(classes="pane"):
                yield Static("Remote", classes="pane-header remote-header")
                yield Static("Connecting...", id="remote-placeholder")
        yield TransferProgress(id="transfer-progress")
        yield Static(
            " [c]opy  [Tab] switch pane  [Esc] back",
            id="ft-status",
        )

    def on_mount(self) -> None:
        self.query_one("#transfer-progress").display = False
        self.query_one("#local-tree").focus()
        self._init_sftp()

    @work(thread=True)
    def _init_sftp(self) -> None:
        try:
            sftp = self.app.ssh_manager.open_sftp(self.connection.id)
            self._sftp_manager = SFTPManager(sftp)
            self.app.call_from_thread(self._mount_remote_tree)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"SFTP error: {e}", severity="error")

    def _mount_remote_tree(self) -> None:
        placeholder = self.query_one("#remote-placeholder", Static)
        remote_pane = placeholder.parent
        placeholder.remove()
        tree = RemoteFileTree(self._sftp_manager, id="remote-tree")
        remote_pane.mount(tree)

    def action_go_back(self) -> None:
        if self._sftp_manager:
            self._sftp_manager.close()
        self.app.pop_screen()

    def action_switch_pane(self) -> None:
        if self._active_pane == "local":
            remote = self.query("RemoteFileTree")
            if remote:
                remote.first().focus()
                self._active_pane = "remote"
        else:
            self.query_one("#local-tree").focus()
            self._active_pane = "local"

    def action_copy_file(self) -> None:
        if not self._sftp_manager:
            self.notify("SFTP not connected", severity="warning")
            return

        if self._active_pane == "local":
            self._upload_selected()
        else:
            self._download_selected()

    def _upload_selected(self) -> None:
        tree = self.query_one("#local-tree", DirectoryTree)
        node = tree.cursor_node
        if not node or not node.data:
            self.notify("No file selected", severity="warning")
            return
        local_path = str(node.data.path)
        if os.path.isdir(local_path):
            self.notify("Cannot upload directories (select a file)", severity="warning")
            return
        filename = os.path.basename(local_path)
        remote_cwd = self._sftp_manager.cwd()
        remote_path = remote_cwd.rstrip("/") + "/" + filename
        self._do_upload(local_path, remote_path)

    @work(thread=True)
    def _do_upload(self, local_path: str, remote_path: str) -> None:
        filename = os.path.basename(local_path)
        total = os.path.getsize(local_path)
        self.app.call_from_thread(self._start_progress, filename, total)

        def callback(transferred, total_bytes):
            self.app.call_from_thread(self._update_progress, transferred, total_bytes)

        try:
            self._sftp_manager.upload(local_path, remote_path, callback=callback)
            self.app.call_from_thread(self._finish_progress)
            self.app.call_from_thread(self.notify, f"Uploaded {filename}")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Upload failed: {e}", severity="error")

    def _download_selected(self) -> None:
        remote_trees = self.query("RemoteFileTree")
        if not remote_trees:
            return
        tree = remote_trees.first()
        node = tree.cursor_node
        if not node or not node.data:
            self.notify("No file selected", severity="warning")
            return
        remote_path = node.data
        filename = os.path.basename(remote_path)
        local_path = str(Path.home() / "Downloads" / filename)
        self._do_download(remote_path, local_path)

    @work(thread=True)
    def _do_download(self, remote_path: str, local_path: str) -> None:
        filename = os.path.basename(remote_path)
        stat = self._sftp_manager.stat(remote_path)
        total = stat.st_size if stat and stat.st_size else 0
        self.app.call_from_thread(self._start_progress, filename, total)

        def callback(transferred, total_bytes):
            self.app.call_from_thread(self._update_progress, transferred, total_bytes)

        try:
            self._sftp_manager.download(remote_path, local_path, callback=callback)
            self.app.call_from_thread(self._finish_progress)
            self.app.call_from_thread(self.notify, f"Downloaded to {local_path}")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Download failed: {e}", severity="error")

    def _start_progress(self, filename: str, total: int) -> None:
        progress = self.query_one("#transfer-progress", TransferProgress)
        progress.start(filename, total)

    def _update_progress(self, transferred: int, total: int) -> None:
        progress = self.query_one("#transfer-progress", TransferProgress)
        progress.update_progress(transferred, total)

    def _finish_progress(self) -> None:
        progress = self.query_one("#transfer-progress", TransferProgress)
        progress.finish()
