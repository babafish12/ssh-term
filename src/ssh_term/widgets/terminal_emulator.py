"""Terminal emulator widget using pyte + paramiko."""

from __future__ import annotations

import threading

import paramiko
import pyte
from rich.text import Text
from textual import work
from textual.widgets import Static
from textual.events import Key, Resize

from ssh_term.theme import TERMINAL_FG, TERMINAL_BG, TERMINAL_ANSI


_PYTE_COLOR_MAP = {
    "black": TERMINAL_ANSI[0],
    "red": TERMINAL_ANSI[1],
    "green": TERMINAL_ANSI[2],
    "brown": TERMINAL_ANSI[3],
    "blue": TERMINAL_ANSI[4],
    "magenta": TERMINAL_ANSI[5],
    "cyan": TERMINAL_ANSI[6],
    "white": TERMINAL_ANSI[7],
    "brightblack": TERMINAL_ANSI[8],
    "brightred": TERMINAL_ANSI[9],
    "brightgreen": TERMINAL_ANSI[10],
    "brightyellow": TERMINAL_ANSI[11],
    "brightblue": TERMINAL_ANSI[12],
    "brightmagenta": TERMINAL_ANSI[13],
    "brightcyan": TERMINAL_ANSI[14],
    "brightwhite": TERMINAL_ANSI[15],
}


def _resolve_color(color: str, default: str) -> str:
    if not color or color == "default":
        return default
    if color in _PYTE_COLOR_MAP:
        return _PYTE_COLOR_MAP[color]
    if len(color) == 6:
        try:
            int(color, 16)
            return f"#{color}"
        except ValueError:
            pass
    return default


class TerminalEmulator(Static):
    DEFAULT_CSS = """
    TerminalEmulator {
        width: 1fr;
        height: 1fr;
        overflow: hidden;
        background: """ + TERMINAL_BG + """;
    }
    """

    def __init__(self, channel: paramiko.Channel, **kwargs) -> None:
        super().__init__(**kwargs)
        self.channel = channel
        self._cols = 80
        self._rows = 24
        self._pyte_screen = pyte.Screen(self._cols, self._rows)
        self.stream = pyte.Stream(self._pyte_screen)
        self._stop_event = threading.Event()
        self.can_focus = True

    def on_mount(self) -> None:
        self._read_channel()

    @work(thread=True)
    def _read_channel(self) -> None:
        while not self._stop_event.is_set():
            try:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096)
                    if not data:
                        break
                    self.stream.feed(data.decode("utf-8", errors="replace"))
                    self.app.call_from_thread(self._refresh_content)
                elif self.channel.exit_status_ready():
                    break
                else:
                    self._stop_event.wait(0.02)
            except Exception:
                break
        self.app.call_from_thread(self._on_disconnect)

    def _on_disconnect(self) -> None:
        from textual.message import Message

        class Disconnected(Message):
            pass

        self.post_message(Disconnected())

    def _refresh_content(self) -> None:
        self.update(self._render_screen())

    def _render_screen(self) -> Text:
        text = Text()
        cursor = self._pyte_screen.cursor
        for y in range(self._pyte_screen.lines):
            line = self._pyte_screen.buffer[y]
            for x in range(self._pyte_screen.columns):
                char = line[x]
                ch = char.data or " "
                fg = _resolve_color(char.fg, TERMINAL_FG)
                bg = _resolve_color(char.bg, TERMINAL_BG)
                style = f"{fg} on {bg}"
                if char.bold:
                    style += " bold"
                if char.italics:
                    style += " italic"
                if char.underscore:
                    style += " underline"
                if y == cursor.y and x == cursor.x:
                    style = f"{bg} on {fg}"
                text.append(ch, style=style)
            if y < self._pyte_screen.lines - 1:
                text.append("\n")
        return text

    def on_key(self, event: Key) -> None:
        event.stop()
        event.prevent_default()
        key = event.key

        key_map = {
            "escape": "\x1b",
            "enter": "\r",
            "tab": "\t",
            "backspace": "\x7f",
            "delete": "\x1b[3~",
            "up": "\x1b[A",
            "down": "\x1b[B",
            "right": "\x1b[C",
            "left": "\x1b[D",
            "home": "\x1b[H",
            "end": "\x1b[F",
            "pageup": "\x1b[5~",
            "pagedown": "\x1b[6~",
            "insert": "\x1b[2~",
            "f1": "\x1bOP",
            "f2": "\x1bOQ",
            "f3": "\x1bOR",
            "f4": "\x1bOS",
            "f5": "\x1b[15~",
            "f6": "\x1b[17~",
            "f7": "\x1b[18~",
            "f8": "\x1b[19~",
            "f9": "\x1b[20~",
            "f10": "\x1b[21~",
            "f11": "\x1b[23~",
            "f12": "\x1b[24~",
        }

        data: str | None = None
        if key in key_map:
            data = key_map[key]
        elif key.startswith("ctrl+") and len(key) == 6:
            ch = key[-1]
            code = ord(ch.lower()) - ord("a") + 1
            data = chr(code)
        elif event.character:
            data = event.character

        if data:
            try:
                self.channel.send(data.encode())
            except Exception:
                pass

    def on_resize(self, event: Resize) -> None:
        cols = max(event.size.width, 1)
        rows = max(event.size.height, 1)
        if cols != self._cols or rows != self._rows:
            self._cols = cols
            self._rows = rows
            self._pyte_screen.resize(rows, cols)
            try:
                self.channel.resize_pty(width=cols, height=rows)
            except Exception:
                pass

    def stop(self) -> None:
        self._stop_event.set()
        try:
            self.channel.close()
        except Exception:
            pass
