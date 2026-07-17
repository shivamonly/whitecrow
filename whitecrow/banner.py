import time
import shutil
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.align import Center

console = Console()

FRAME_A = [
    "        ▄▄▄              ▄▄▄        ",
    "       █▓▓▓█            █▓▓▓█       ",
    "      █▓▓▓▓▓█          █▓▓▓▓▓█      ",
    "  ▄▄  █▓ ● ▓█  🚬  ▄▄  █▓ ● ▓█  🚬 ",
    " █  █ █▓ V ▓█ ~~~ █  █ █▓ V ▓█ ~~~  ",
    " █  █ █▓   ▓█  ~~ █  █ █▓   ▓█  ~~  ",
    " █  █ █▓▓▓▓▓█  ~~ █  █ █▓▓▓▓▓█  ~~  ",
    "  █  ██▓▓▓█      █  ██▓▓▓█         ",
    "   █  █  █        █  █  █           ",
    "     █  █           █  █            ",
    "    ╱█  █╲         ╱█  █╲           ",
    "   ╱ █  █ ╲       ╱ █  █ ╲          ",
]

FRAME_B = [
    "        ▄▄▄              ▄▄▄        ",
    "       █▓▓▓█            █▓▓▓█       ",
    "      █▓▓▓▓▓█          █▓▓▓▓▓█      ",
    "  ▄▄  █▓ ○ ▓█  🚬  ▄▄  █▓ ○ ▓█  🚬 ",
    " █  █ █▓ V ▓█ ~~~ █  █ █▓ V ▓█ ~~~  ",
    " █  █ █▓   ▓█  ~~ █  █ █▓   ▓█  ~~  ",
    " █  █ █▓▓▓▓▓█  ~~ █  █ █▓▓▓▓▓█  ~~  ",
    "  █  ██▓▓▓█      █  ██▓▓▓█         ",
    "   █  █  █        █  █  █           ",
    "     █  █           █  █            ",
    "    ╱█  █╲         ╱█  █╲           ",
    "   ╱ █  █ ╲       ╱ █  █ ╲          ",
]

FRAME_C = [
    "  ▄▄     ▄▄▄       ▄▄     ▄▄▄       ",
    " █  █   █▓▓▓█     █  █   █▓▓▓█      ",
    " █  █  █▓▓▓▓▓█    █  █  █▓▓▓▓▓█     ",
    " █  █  █▓ ● ▓█ 🚬 █  █  █▓ ● ▓█ 🚬  ",
    " █  █  █▓ V ▓█ ~~ █  █  █▓ V ▓█ ~~  ",
    "  █  █ █▓   ▓█  ~  █  █ █▓   ▓█  ~  ",
    "  █  █ █▓▓▓▓▓█  ~  █  █ █▓▓▓▓▓█  ~  ",
    "   █  ██▓▓▓█       █  ██▓▓▓█        ",
    "    █  █  █         █  █  █          ",
    "      █  █            █  █           ",
    "     ╱█  █╲          ╱█  █╲          ",
    "    ╱ █  █ ╲        ╱ █  █ ╲         ",
]

FRAMES = [FRAME_A, FRAME_B, FRAME_C, FRAME_B]


def animate_banner(duration=2.5):
    cols, _ = shutil.get_terminal_size()
    n_frames = len(FRAMES)
    repeats = max(4, int(duration / (n_frames * 0.08)))

    with Live(console=console, refresh_per_second=16, transient=True, screen=False) as live:
        for r in range(repeats):
            for fi, frame in enumerate(FRAMES):
                smoke_char = ["▓", "▒", "░", " "][(r + fi) % 4]
                lines = list(frame)
                for li in range(len(lines)):
                    l = lines[li]
                    idx = l.find("~")
                    if idx >= 0:
                        lst = list(l)
                        for si in range(min(3, len(lst) - idx)):
                            if lst[idx + si] == "~":
                                pass
                        lines[li] = l.replace("~~~", f"{smoke_char}{smoke_char}{smoke_char}").replace("~~", f"{smoke_char}{smoke_char}").replace("~", smoke_char)

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
