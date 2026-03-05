"""Configuration manager — JSON persistence."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from ssh_term.models.connection import SSHConnection

CONFIG_DIR = Path.home() / ".config" / "ssh-term"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _default_config() -> dict:
    return {
        "version": 1,
        "master_password_hash": "",
        "salt": "",
        "connections": [],
    }


class ConfigManager:
    def __init__(self, path: Path = CONFIG_FILE) -> None:
        self.path = path
        self._data: dict = _default_config()

    def load(self) -> None:
        if self.path.exists():
            self._data = json.loads(self.path.read_text())
        else:
            self._data = _default_config()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))

    @property
    def is_first_run(self) -> bool:
        return not self._data.get("master_password_hash")

    @property
    def master_password_hash(self) -> str:
        return self._data.get("master_password_hash", "")

    @master_password_hash.setter
    def master_password_hash(self, value: str) -> None:
        self._data["master_password_hash"] = value

    @property
    def salt(self) -> bytes:
        encoded = self._data.get("salt", "")
        if encoded:
            return base64.b64encode(base64.b64decode(encoded))[:16]
        return b""

    @property
    def salt_bytes(self) -> bytes:
        encoded = self._data.get("salt", "")
        return base64.b64decode(encoded) if encoded else b""

    @salt_bytes.setter
    def salt_bytes(self, value: bytes) -> None:
        self._data["salt"] = base64.b64encode(value).decode()

    @property
    def connections(self) -> list[SSHConnection]:
        return [SSHConnection.from_dict(c) for c in self._data.get("connections", [])]

    @connections.setter
    def connections(self, conns: list[SSHConnection]) -> None:
        self._data["connections"] = [c.to_dict() for c in conns]

    def add_connection(self, conn: SSHConnection) -> None:
        conns = self.connections
        conns.append(conn)
        self.connections = conns
        self.save()

    def update_connection(self, conn: SSHConnection) -> None:
        conns = self.connections
        for i, c in enumerate(conns):
            if c.id == conn.id:
                conns[i] = conn
                break
        self.connections = conns
        self.save()

    def delete_connection(self, conn_id: str) -> None:
        conns = [c for c in self.connections if c.id != conn_id]
        self.connections = conns
        self.save()

    def get_connection(self, conn_id: str) -> SSHConnection | None:
        for c in self.connections:
            if c.id == conn_id:
                return c
        return None
