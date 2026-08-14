"""Terminal styling, ASCII tables, and formatting utilities."""

from __future__ import annotations

import sys
from typing import Any, List, Optional, Sequence


class Colors:
    """ANSI color escape sequences."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @classmethod
    def colorize(cls, text: str, color_code: str) -> str:
        if not sys.stdout.isatty():
            return text
        return f"{color_code}{text}{cls.RESET}"


def bold(text: Any) -> str:
    return Colors.colorize(str(text), Colors.BOLD)


def green(text: Any) -> str:
    return Colors.colorize(str(text), Colors.GREEN)


def yellow(text: Any) -> str:
    return Colors.colorize(str(text), Colors.YELLOW)


def cyan(text: Any) -> str:
    return Colors.colorize(str(text), Colors.CYAN)


def red(text: Any) -> str:
    return Colors.colorize(str(text), Colors.RED)


def blue(text: Any) -> str:
    return Colors.colorize(str(text), Colors.BLUE)


def magenta(text: Any) -> str:
    return Colors.colorize(str(text), Colors.MAGENTA)


def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print an eye-catching terminal header banner."""
    width = max(len(title), len(subtitle or "")) + 8
    width = max(width, 60)
    border = "=" * width

    print()
    print(cyan(border))
    print(f"{bold(cyan('  ' + title.center(width - 4)))}")
    if subtitle:
        print(f"{Colors.colorize('  ' + subtitle.center(width - 4), Colors.DIM)}")
    print(cyan(border))
    print()


def print_section(title: str) -> None:
    """Print a clean section heading."""
    print(f"\n{bold(yellow('>>> ' + title))}")
    print(yellow("-" * (len(title) + 4)))


def format_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    alignments: Optional[Sequence[str]] = None,
) -> str:
    """Generate a clean, aligned ASCII table without external dependencies.

    Args:
        headers: List of column header names.
        rows: 2D list of row values.
        alignments: List of alignment codes ('left', 'right', 'center').

    Returns:
        Formatted ASCII table string.
    """
    if not headers and not rows:
        return ""

    num_cols = len(headers)
    col_widths = [len(h) for h in headers]

    str_rows: List[List[str]] = []
    for r in rows:
        s_row = [str(cell) for cell in r]
        str_rows.append(s_row)
        for i, val in enumerate(s_row):
            if i < num_cols:
                col_widths[i] = max(col_widths[i], len(val))

    aligns = alignments or ["left"] * num_cols

    # Formatting helper
    def pad(text: str, width: int, align: str) -> str:
        if align == "right":
            return text.rjust(width)
        elif align == "center":
            return text.center(width)
        return text.ljust(width)

    # Build ASCII components
    sep_top = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    sep_mid = "+=" + "=+=".join("=" * w for w in col_widths) + "=+"
    sep_bot = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    header_line = "| " + " | ".join(pad(bold(h), col_widths[i], aligns[i]) for i, h in enumerate(headers)) + " |"

    body_lines: List[str] = []
    for row in str_rows:
        line = "| " + " | ".join(pad(row[i] if i < len(row) else "", col_widths[i], aligns[i]) for i in range(num_cols)) + " |"
        body_lines.append(line)

    res = [sep_top, header_line, sep_mid]
    res.extend(body_lines)
    res.append(sep_bot)

    return "\n".join(res)


def format_path(path: Sequence[str], arrow: str = " ➔ ") -> str:
    """Format an ordered sequence of station names with colored arrows."""
    if not path:
        return red("(No valid route found)")
    return cyan(arrow).join(bold(st) for st in path)
