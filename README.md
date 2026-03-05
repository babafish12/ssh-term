# SSH Terminal Manager

A minimalistic TUI application for managing and connecting to SSH servers, built with Python and [Textual](https://textual.textualize.io/).

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Connection Management** — Add, edit, and delete SSH connections with a clean dashboard UI
- **Interactive SSH Terminal** — Full terminal emulation powered by pyte with 256-color support
- **Dual-Pane File Transfer** — Browse local and remote filesystems side-by-side, copy files via SFTP
- **Encrypted Storage** — Master password with bcrypt hashing, SSH passwords encrypted with Fernet (PBKDF2-derived key)
- **Tokyo Night Theme** — Dark color scheme inspired by the Tokyo Night palette
- **Multiple Auth Methods** — SSH key, password, or SSH agent authentication

## Installation

```bash
git clone https://github.com/vube/ssh-term.git
cd ssh-term
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
ssh-term
```

On first launch, you'll be prompted to set a master password. This password encrypts any stored SSH passwords and is required on each startup.

### Dashboard Keybindings

| Key     | Action              |
|---------|---------------------|
| `a`     | Add connection      |
| `e`     | Edit connection     |
| `d`     | Delete connection   |
| `Enter` | Connect (SSH)       |
| `f`     | File transfer       |
| `q`     | Quit                |

### Terminal Keybindings

| Key      | Action                |
|----------|-----------------------|
| `Ctrl+D` | Disconnect            |
| `Ctrl+F` | Open file transfer    |

### File Transfer Keybindings

| Key     | Action              |
|---------|---------------------|
| `c`     | Copy selected file  |
| `Tab`   | Switch pane         |
| `Esc`   | Go back             |

## Configuration

All data is stored in `~/.config/ssh-term/config.json`:

- Master password hash (bcrypt)
- Encryption salt
- SSH connections (passwords encrypted with Fernet)

## Architecture

```
src/ssh_term/
├── app.py                    # Textual App + theme
├── theme.py                  # Tokyo Night color scheme
├── models/
│   ├── connection.py         # SSHConnection dataclass
│   ├── config.py             # JSON config persistence
│   └── auth.py               # bcrypt + Fernet encryption
├── screens/
│   ├── auth_screen.py        # Master password login
│   ├── dashboard.py          # Connection list
│   ├── connection_form.py    # Add/Edit modal
│   ├── confirm_dialog.py     # Delete confirmation
│   ├── terminal_screen.py    # SSH terminal
│   └── file_transfer.py      # Dual-pane SFTP browser
├── widgets/
│   ├── terminal_emulator.py  # pyte + paramiko terminal
│   ├── connection_table.py   # Styled DataTable
│   ├── remote_file_tree.py   # Lazy-loading SFTP tree
│   └── transfer_progress.py  # Transfer progress bar
└── services/
    ├── ssh_manager.py        # SSH connection lifecycle
    └── sftp_manager.py       # SFTP operations
```

## Dependencies

- [textual](https://textual.textualize.io/) — TUI framework
- [rich](https://rich.readthedocs.io/) — Terminal rendering
- [paramiko](https://www.paramiko.org/) — SSH protocol
- [pyte](https://pyte.readthedocs.io/) — Terminal emulation
- [bcrypt](https://github.com/pyca/bcrypt) — Password hashing
- [cryptography](https://cryptography.io/) — Fernet encryption
