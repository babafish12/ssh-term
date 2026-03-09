# SSH Terminal Manager

A minimalistic TUI application for managing and connecting to SSH servers, built with Python and [Textual](https://textual.textualize.io/).

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Connection Management** — Add, edit, and delete SSH connections from a central dashboard with a sortable table view
- **Interactive Terminal** — Full-screen SSH terminal emulation powered by [pyte](https://pyte.readthedocs.io/) with xterm-256color support, cursor rendering, and automatic terminal resizing
- **Dual-Pane File Transfer** — Side-by-side local and remote filesystem browser via SFTP with progress bar for uploads and downloads
- **Encrypted Password Storage** — Master password hashed with bcrypt (480k iterations). SSH passwords encrypted with Fernet, using a PBKDF2-derived key (SHA-256, 480k iterations) from the master password
- **Tokyo Night Theme** — Dark color scheme inspired by the [Tokyo Night](https://github.com/enkia/tokyo-night-vscode-theme) palette
- **Multiple Auth Methods** — SSH key, password, or SSH agent authentication
- **Lazy-Loading Remote Tree** — Remote directories are only fetched when expanded, keeping the UI responsive on large filesystems
- **Persistent Configuration** — All connections stored in a single JSON file, easy to back up or migrate

---

## Prerequisites

- Python 3.11+
- [pipx](https://pipx.pypa.io/) (recommended) or pip

---

## Installation

```bash
git clone https://github.com/babafish12/ssh-term.git
cd ssh-term
pipx install .
```

This installs `ssh-term` globally in an isolated virtual environment managed by pipx. The `ssh-term` command will be available system-wide at `~/.local/bin/ssh-term`.

### Updating

```bash
cd ssh-term
git pull
pipx install . --force
```

### Uninstalling

```bash
pipx uninstall ssh-term
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

On first launch you'll be prompted to create a master password. You need to enter it twice for confirmation. This password:

- Is hashed with **bcrypt** and stored in the config file (never in plaintext)
- Derives an encryption key via **PBKDF2** (SHA-256, 480k iterations) used to encrypt/decrypt any saved SSH passwords
- Is required on every startup to unlock the application

### 2. Add a Connection

Press `a` on the dashboard to open the Add Connection form:

| Field              | Required | Description                                      |
|--------------------|----------|--------------------------------------------------|
| **Name**           | Yes      | Display name shown in the dashboard table        |
| **IP**             | Yes      | Hostname or IP address of the SSH server         |
| **Port**           | No       | SSH port (default: `22`)                         |
| **Username**       | Yes      | SSH login username                               |
| **Auth Method**    | Yes      | `SSH Key`, `Password`, or `SSH Agent`            |
| **Private Key Path** | No     | Path to private key (default: `~/.ssh/id_ed25519`). Only used with SSH Key auth |
| **Password**       | No       | SSH password, stored encrypted with Fernet. Only used with Password auth |
| **Tags**           | No       | Comma-separated labels for organization (e.g. `prod, web, db`) |

Connections are saved immediately to `~/.config/ssh-term/config.json`.

### 3. Connect

Navigate connections with `Up`/`Down` arrow keys, then press `Enter` or click a row to connect. A full-screen interactive SSH terminal opens with:

- 256-color rendering
- Cursor display
- Automatic terminal resize (syncs pyte screen + remote PTY)
- Support for function keys (F1-F12), arrow keys, Home/End, PageUp/PageDown, Insert, Delete
- A status bar at the bottom showing the connection name, host, and available shortcuts

### 4. File Transfer

Press `f` on the dashboard (connects automatically if needed) or `Ctrl+F` inside an active terminal session to open the dual-pane file browser:

- **Left pane:** Local filesystem (starts at `$HOME`)
- **Right pane:** Remote filesystem via SFTP (lazy-loaded, starts at remote home directory)
- **Upload:** Select a file in the local pane, press `c` — file is uploaded to the remote working directory
- **Download:** Switch to the remote pane with `Tab`, select a file, press `c` — file is downloaded to `~/Downloads/`
- A **progress bar** at the bottom shows transfer status with filename and progress percentage

---

## Keybindings

### Dashboard

| Key           | Action                             |
|---------------|------------------------------------|
| `Up` / `Down` | Navigate connections               |
| `a`           | Add new connection                 |
| `e`           | Edit selected connection           |
| `d`           | Delete selected connection (with confirmation dialog) |
| `Enter`       | Connect to selected server via SSH |
| `f`           | Open file transfer for selected server |
| `q`           | Quit the application               |
| Mouse click   | Select row / double-click to connect |

### Terminal

| Key      | Action                                      |
|----------|---------------------------------------------|
| `Ctrl+D` | Disconnect and return to dashboard          |
| `Ctrl+F` | Open file transfer (keeps SSH session alive) |
| All keys | Passed through to the remote shell          |

### File Transfer

| Key     | Action                                          |
|---------|-------------------------------------------------|
| `c`     | Copy selected file (upload or download depending on active pane) |
| `Tab`   | Switch between local and remote pane            |
| `Esc`   | Close file transfer and go back                 |

---

## Screen Flow

```
App Start
  └─> Auth Screen (modal)
        ├─ First run: Set master password (enter twice)
        └─ Subsequent runs: Enter master password
              └─> Dashboard
                    ├─ [a] Add Connection ──> Connection Form (modal)
                    ├─ [e] Edit Connection ─> Connection Form (prefilled, modal)
                    ├─ [d] Delete ──────────> Confirm Dialog (modal)
                    ├─ [Enter] Connect ────> Terminal Screen (full-screen)
                    │                           ├─ Ctrl+D ──> back to Dashboard
                    │                           └─ Ctrl+F ──> File Transfer
                    ├─ [f] File Transfer ──> File Transfer Screen
                    │                           └─ Esc ─────> back to Dashboard
                    └─ [q] Quit
```

---

## Configuration

All data is stored in a single JSON file:

```
~/.config/ssh-term/config.json
```

The directory is created automatically on first run. Example structure:

```json
{
  "version": 1,
  "master_password_hash": "$2b$12$...",
  "salt": "base64-encoded-16-byte-salt",
  "connections": [
    {
      "id": "uuid-v4",
      "name": "Prod Server",
      "host": "192.168.1.50",
      "ip": "",
      "port": 22,
      "username": "deploy",
      "auth_method": "key",
      "private_key_path": "~/.ssh/id_ed25519",
      "password_encrypted": "",
      "tags": ["prod", "web"],
      "color_label": "blue",
      "last_connected": "2026-03-09T14:30:00.000000"
    }
  ]
}
```

### Security Details

| Component         | Algorithm                          | Details                           |
|-------------------|------------------------------------|-----------------------------------|
| Master password   | bcrypt                             | Salted hash, stored in config     |
| Encryption key    | PBKDF2-HMAC-SHA256                 | 480,000 iterations, 16-byte salt  |
| SSH passwords     | Fernet (AES-128-CBC + HMAC-SHA256) | Encrypted with derived key        |

The master password is **never** stored in plaintext. SSH passwords are only decryptable with the correct master password.

### Backup & Migration

To back up or migrate your connections, simply copy `~/.config/ssh-term/config.json`. Note that encrypted passwords can only be decrypted with the same master password.

---

## Project Structure

```
src/ssh_term/
├── __init__.py
├── __main__.py               # Entry point (ssh-term command)
├── app.py                    # Textual App, global CSS, screen flow
├── theme.py                  # Tokyo Night color constants + ANSI mapping
├── models/
│   ├── connection.py         # SSHConnection dataclass + JSON serialization
│   ├── config.py             # ConfigManager — JSON read/write at ~/.config/ssh-term/
│   └── auth.py               # AuthManager — bcrypt hashing + Fernet encrypt/decrypt
├── screens/
│   ├── auth_screen.py        # Master password setup (first run) / login (modal)
│   ├── dashboard.py          # Main view — connection table + hint bar
│   ├── connection_form.py    # Add/Edit connection modal with validation
│   ├── confirm_dialog.py     # Delete confirmation modal
│   ├── terminal_screen.py    # Full-screen SSH terminal with status bar
│   └── file_transfer.py      # Dual-pane SFTP browser with progress bar
├── widgets/
│   ├── terminal_emulator.py  # pyte Screen + paramiko Channel → Rich Text rendering
│   ├── connection_table.py   # Styled DataTable with row cursor + zebra stripes
│   ├── remote_file_tree.py   # Lazy-loading SFTP directory tree
│   └── transfer_progress.py  # File transfer progress bar widget
├── services/
│   ├── ssh_manager.py        # SSH connection lifecycle (connect/shell/sftp/disconnect)
│   └── sftp_manager.py       # SFTP operations (list/upload/download/mkdir/remove)
└── styles/                   # TCSS stylesheets
```

---

## Dependencies

| Package                                          | Purpose                                    |
|--------------------------------------------------|--------------------------------------------|
| [textual](https://textual.textualize.io/) >= 1.0 | TUI framework (widgets, screens, styling)  |
| [rich](https://rich.readthedocs.io/) >= 13.0     | Terminal text rendering                    |
| [paramiko](https://www.paramiko.org/) >= 3.4     | SSH2 protocol (connections, shells, SFTP)  |
| [pyte](https://pyte.readthedocs.io/) >= 0.8.2   | VT100/xterm terminal emulation            |
| [bcrypt](https://github.com/pyca/bcrypt) >= 4.0  | Password hashing                          |
| [cryptography](https://cryptography.io/) >= 42.0 | Fernet symmetric encryption + PBKDF2      |

---

## Troubleshooting

### `ssh-term` command not found after pipx install

Make sure `~/.local/bin` is in your `$PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this line to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Connection fails with "No such file" for SSH key

The default key path is `~/.ssh/id_ed25519`. If you use a different key type, update the **Private Key Path** field when adding the connection (e.g. `~/.ssh/id_rsa`).

### Terminal rendering looks wrong

Make sure your terminal emulator supports 256 colors. The SSH session uses `xterm-256color` as the terminal type.

### Forgot master password

There is no password recovery. Delete `~/.config/ssh-term/config.json` and start fresh. All saved connections and encrypted passwords will be lost.

---

## License

MIT
