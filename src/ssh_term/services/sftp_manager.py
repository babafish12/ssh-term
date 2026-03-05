"""SFTP file transfer operations."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path

import paramiko


@dataclass
class RemoteEntry:
    name: str
    path: str
    is_dir: bool
    size: int = 0
    mtime: float = 0


class SFTPManager:
    def __init__(self, sftp: paramiko.SFTPClient) -> None:
        self.sftp = sftp

    def listdir(self, remote_path: str) -> list[RemoteEntry]:
        entries: list[RemoteEntry] = []
        try:
            for attr in self.sftp.listdir_attr(remote_path):
                is_dir = stat.S_ISDIR(attr.st_mode or 0)
                full = remote_path.rstrip("/") + "/" + attr.filename
                entries.append(
                    RemoteEntry(
                        name=attr.filename,
                        path=full,
                        is_dir=is_dir,
                        size=attr.st_size or 0,
                        mtime=attr.st_mtime or 0,
                    )
                )
        except IOError:
            pass
        entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))
        return entries

    def download(
        self,
        remote_path: str,
        local_path: str,
        callback: callable | None = None,
    ) -> None:
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        self.sftp.get(remote_path, local_path, callback=callback)

    def upload(
        self,
        local_path: str,
        remote_path: str,
        callback: callable | None = None,
    ) -> None:
        self.sftp.put(local_path, remote_path, callback=callback)

    def mkdir(self, remote_path: str) -> None:
        try:
            self.sftp.mkdir(remote_path)
        except IOError:
            pass

    def remove(self, remote_path: str) -> None:
        self.sftp.remove(remote_path)

    def stat(self, remote_path: str) -> paramiko.SFTPAttributes | None:
        try:
            return self.sftp.stat(remote_path)
        except IOError:
            return None

    def cwd(self) -> str:
        return self.sftp.normalize(".")

    def close(self) -> None:
        self.sftp.close()
