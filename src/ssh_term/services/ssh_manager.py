"""SSH connection lifecycle management."""

from __future__ import annotations

import os
from pathlib import Path

import paramiko

from ssh_term.models.connection import SSHConnection


class SSHManager:
    def __init__(self) -> None:
        self._clients: dict[str, paramiko.SSHClient] = {}

    def connect(
        self,
        conn: SSHConnection,
        password: str | None = None,
    ) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs: dict = {
            "hostname": conn.host,
            "port": conn.port,
            "username": conn.username,
            "timeout": 10,
        }

        if conn.auth_method == "key":
            key_path = os.path.expanduser(conn.private_key_path)
            if Path(key_path).exists():
                connect_kwargs["key_filename"] = key_path
            else:
                connect_kwargs["look_for_keys"] = True
        elif conn.auth_method == "password" and password:
            connect_kwargs["password"] = password
        elif conn.auth_method == "agent":
            connect_kwargs["allow_agent"] = True

        client.connect(**connect_kwargs)
        self._clients[conn.id] = client
        return client

    def get_client(self, conn_id: str) -> paramiko.SSHClient | None:
        return self._clients.get(conn_id)

    def open_shell(
        self, conn_id: str, cols: int = 80, rows: int = 24
    ) -> paramiko.Channel:
        client = self._clients.get(conn_id)
        if not client:
            raise RuntimeError(f"No active connection for {conn_id}")
        channel = client.invoke_shell(
            term="xterm-256color", width=cols, height=rows
        )
        channel.settimeout(0.0)
        return channel

    def open_sftp(self, conn_id: str) -> paramiko.SFTPClient:
        client = self._clients.get(conn_id)
        if not client:
            raise RuntimeError(f"No active connection for {conn_id}")
        return client.open_sftp()

    def disconnect(self, conn_id: str) -> None:
        client = self._clients.pop(conn_id, None)
        if client:
            client.close()

    def disconnect_all(self) -> None:
        for client in self._clients.values():
            client.close()
        self._clients.clear()

    def is_connected(self, conn_id: str) -> bool:
        client = self._clients.get(conn_id)
        if not client:
            return False
        transport = client.get_transport()
        return transport is not None and transport.is_active()
