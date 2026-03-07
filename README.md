# SSH Terminal Manager

A minimalistic TUI application for managing and connecting to SSH servers, built with Python and [Textual](https://textual.textualize.io/).

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Connection Management** — Add, edit, and delete SSH connections with a clean dashboard UI
- **Interactive Terminal** — Full terminal emulation with 256-color support (pyte)
- **File Transfer** — Dual-pane browser for local and remote filesystems via SFTP
- **Encrypted Storage** — Master password (bcrypt), SSH passwords encrypted with Fernet (PBKDF2)
- **Tokyo Night Theme** — Dark color scheme inspired by the Tokyo Night palette
- **Multiple Auth Methods** — SSH key, password, or SSH agent

---

## Prerequisites

- Python 3.11+
- [pipx](https://pipx.pypa.io/) (recommended) or pip

## Installation

```bash
git clone https://github.com/babafish12/ssh-term.git
cd ssh-term
pipx install .
```

This installs `ssh-term` globally in an isolated environment. The `ssh-term` command will be available system-wide.

### Updating

```bash
cd ssh-term
git pull
pipx install . --force
```

<details>
<summary>Alternative: install in a virtual environment (for development)</summary>

```bash
git clone https://github.com/babafish12/ssh-term.git
cd ssh-term
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

</details>

---

## Quick Start

```bash
ssh-term
```

### 1. Set a Master Password

On first launch you'll be prompted to create a master password. This password encrypts all stored SSH passwords and is required on every startup.

### 2. Add a Connection

Press `a` on the dashboard to add a new connection. The following fields are available:

| Field            | Description                                    |
|------------------|------------------------------------------------|
| Name             | Display name (e.g. "Prod Server")              |
| IP               | Hostname or IP address                         |
| Port             | SSH port (default: 22)                         |
| Username         | SSH username                                   |
| Auth Method      | `SSH Key`, `Password`, or `SSH Agent`          |
| Private Key Path | Path to private key (default: `~/.ssh/id_ed25519`) |
| Password         | SSH password (stored encrypted)                |
| Tags             | Comma-separated tags (e.g. "prod, web")        |

### 3. Connect

Navigate connections with arrow keys (`Up`/`Down`), then press `Enter` or click a row to connect. An interactive SSH terminal opens.

### 4. File Transfer

Press `f` on the dashboard or `Ctrl+F` inside the terminal to open the dual-pane file browser. The left pane shows local files, the right pane shows the remote filesystem via SFTP.

- **Upload:** Select a file in the left pane and press `c`
- **Download:** Select a file in the right pane and press `c` (saved to `~/Downloads`)
- Switch between panes with `Tab`

---

## Keybindings

### Dashboard

| Key        | Action                |
|------------|-----------------------|
| `Up/Down`  | Navigate connections  |
| `a`        | Add connection        |
| `e`        | Edit connection       |
| `d`        | Delete connection     |
| `Enter`    | Connect (SSH)         |
| `f`        | Open file transfer    |
| `q`        | Quit                  |
| Mouse click | Select row / connect |

### Terminal

| Key      | Action              |
|----------|---------------------|
| `Ctrl+D` | Disconnect          |
| `Ctrl+F` | Open file transfer  |

### File Transfer

| Key     | Action              |
|---------|---------------------|
| `c`     | Copy selected file  |
| `Tab`   | Switch pane         |
| `Esc`   | Go back             |

---

## Configuration

All data is stored in `~/.config/ssh-term/config.json`:

- Master password hash (bcrypt)
- Encryption salt
- SSH connections (passwords encrypted with Fernet)

---

## Project Structure

```
src/ssh_term/
├── app.py                    # Textual App + global styles
├── theme.py                  # Tokyo Night color constants
├── styles/                   # TCSS stylesheets
├── models/
│   ├── connection.py         # SSHConnection dataclass
│   ├── config.py             # JSON config persistence
│   └── auth.py               # bcrypt + Fernet encryption
├── screens/
│   ├── auth_screen.py        # Master password login
│   ├── dashboard.py          # Connection list + hint bar
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
- [paramiko](https://www.paramiko.org/) — SSH protocol
- [pyte](https://pyte.readthedocs.io/) — Terminal emulation
- [bcrypt](https://github.com/pyca/bcrypt) — Password hashing
- [cryptography](https://cryptography.io/) — Fernet encryption

## License

MIT
