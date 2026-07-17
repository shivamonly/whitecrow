import time
import shutil
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.align import Center

console = Console()

FRAME_A = [
    "      .-.           .-.        ",
    "     ( o )──🚬     ( o )──🚬   ",
    "     (   )  ~~     (   )  ~~   ",
    "      '-'   ~~      '-'   ~~   ",
    "     ╱   ╲  ~~     ╱   ╲  ~~   ",
    "    ╱     ╲       ╱     ╲      ",
]

FRAME_B = [
    "      .-.           .-.        ",
    "     ( o )──🚬     ( o )──🚬   ",
    "     (   )  ▓▓     (   )  ▓▓   ",
    "      '-'   ▓▓      '-'   ▓▓   ",
    "     ╱   ╲  ▓▓     ╱   ╲  ▓▓   ",
    "    ╱     ╲       ╱     ╲      ",
]

FRAME_C = [
    "      .-.           .-.        ",
    "     ( ● )──🚬     ( ● )──🚬   ",
    "     (   )  ▒▒     (   )  ▒▒   ",
    "      '-'   ▒▒      '-'   ▒▒   ",
    "     ╱   ╲  ▒▒     ╱   ╲  ▒▒   ",
    "    ╱     ╲       ╱     ╲      ",
]

FRAMES = [FRAME_A, FRAME_A, FRAME_B, FRAME_B, FRAME_C, FRAME_B, FRAME_B]


def animate_banner(duration=2.0):
    cols, _ = shutil.get_terminal_size()
    separators = ["", "", "  ~", "  ~~", "  ~~~", "   ~~", "    ~", "     "]

    with Live(console=console, refresh_per_second=12, transient=True, screen=False) as live:
        for step in range(24):
            fi = step % len(FRAMES)
            frame = FRAMES[fi]
            sep = separators[step % len(separators)]
            lines = list(frame)
            art = "\n".join(lines)
            panel = Panel(
                Center(Text(art, style="bold cyan")),
                width=min(50, cols - 4),
                border_style="bright_magenta",
                title=f"[bright_magenta]WhiteCrow v1.0.0[/]",
                subtitle="[dim]OSINT Investigation Tool[/]",
                padding=(0, 2),
            )
            live.update(panel)
            time.sleep(0.08)

    show_banner()


def show_banner():
    cols, _ = shutil.get_terminal_size()
    art = "\n".join(FRAME_A)
    panel = Panel(
        Center(Text(art, style="bold cyan")),
        width=min(50, cols - 4),
        border_style="bright_cyan",
        title=f"[bright_magenta]WhiteCrow v1.0.0[/]",
        subtitle="[dim]OSINT Investigation Tool[/]",
        padding=(0, 2),
    )
    console.print(panel)
