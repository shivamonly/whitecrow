import time
import shutil
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.align import Center
from rich.columns import Columns

console = Console()

CROW = [
    r"                 ╔══════════╗",
    r"                 ║  WHITE   ║",
    r"                 ║  CROW    ║",
    r"                 ║  ┌────┐  ║",
    r"                 ║  │ CIG│  ║",
    r"                 ║  └────┘  ║",
    r"                 ╚══╤══╤═══╝",
    r"                  ╱│  │  ╲",
    r"                 ╱ │  │   ╲",
]

SMOKE_POSITIONS = [
    [6, 23], [5, 24], [4, 25], [3, 26], [2, 25], [1, 24],
]

def animate_banner(duration=2.0):
    cols, _ = shutil.get_terminal_size()
    smoke_chars = ["▓", "▒", "░", " ", " "]
    frames = 20
    delay = duration / frames

    with Live(console=console, refresh_per_second=20, transient=True, screen=False) as live:
        for i in range(frames):
            crow_lines = CROW.copy()
            si = i % len(SMOKE_POSITIONS)
            row, col = SMOKE_POSITIONS[si]
            for r_off in range(3):
                r_idx = row - r_off
                if 0 <= r_idx < len(crow_lines):
                    line = list(crow_lines[r_idx])
                    c_idx = col + r_off
                    if c_idx < len(line):
                        sc = smoke_chars[(i + r_off * 3) % len(smoke_chars)]
                        line[c_idx] = sc
                    if c_idx + 1 < len(line) and line[c_idx + 1] == " ":
                        line[c_idx + 1] = smoke_chars[(i + r_off * 3 + 1) % len(smoke_chars)]
                    crow_lines[r_idx] = "".join(line)

            art = "\n".join(crow_lines)
            panel = Panel(
                Center(Text(art, style="bold cyan")),
                width=min(50, cols - 4),
                border_style="bright_cyan",
                title=f"[bright_magenta]WhiteCrow v1.0.0[/]",
                subtitle="[dim]OSINT Investigation Tool[/]",
                padding=(1, 2),
            )
            live.update(panel)
            time.sleep(delay)

def show_banner():
    cols, _ = shutil.get_terminal_size()
    art = "\n".join(CROW)
    panel = Panel(
        Center(Text(art, style="bold cyan")),
        width=min(50, cols - 4),
        border_style="bright_cyan",
        title=f"[bright_magenta]WhiteCrow v1.0.0[/]",
        subtitle="[dim]OSINT Investigation Tool[/]",
        padding=(1, 2),
    )
    console.print(panel)
