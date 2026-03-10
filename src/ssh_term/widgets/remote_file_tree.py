"""Lazy-loading SFTP remote file tree."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Tree
from textual.widgets._tree import TreeNode

from ssh_term.services.sftp_manager import SFTPManager


class RemoteFileTree(Tree):
    DEFAULT_CSS = """
    RemoteFileTree {
        width: 1fr;
        height: 1fr;
    }
    """

    def __init__(self, sftp_manager: SFTPManager, **kwargs) -> None:
        self._sftp = sftp_manager
        root_path = sftp_manager.cwd()
        super().__init__(root_path, **kwargs)
        self.root.data = root_path

    def on_mount(self) -> None:
        self._load_node(self.root)
        self.root.expand()

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        node = event.node
        if node.data and len(node.children) == 1 and node.children[0].label.plain == "...":
            node.children[0].remove()
            self._load_node(node)

    def _load_node(self, node: TreeNode) -> None:
        path = node.data
        if not path:
            return
        entries = self._sftp.listdir(path)
        for entry in entries:
            if entry.name.startswith("."):
                continue
            if entry.is_dir:
                label = Text(entry.name, style="bold")
                child = node.add(label, data=entry.path)
                child.add_leaf("...", data=None)
            else:
                size = self._format_size(entry.size)
                label = Text.assemble(
                    (entry.name, ""),
                    (f"  ({size})", "dim"),
                )
                node.add_leaf(label, data=entry.path)

    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
