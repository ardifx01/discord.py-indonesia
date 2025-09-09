import logging
import sys
import rich
import pathlib
import datetime

from os import name, system
from rich.text import Text
from rich.style import Style
from rich.theme import Theme
from rich.logging import RichHandler, LogRecord
from rich.console import Console
from logging import handlers

class CustomRichHandler(RichHandler):
    """
    Kelas handler kustom yang memperluas RichHandler untuk menyediakan format log yang kustom.
    """
    def get_level_text(self, record: LogRecord) -> Text:
        """
        Mendapatkan teks level dari catatan dan menebalkan hurufnya.
        """
        level_text = super().get_level_text(record)
        level_text.stylize("bold")
        return level_text

    def emit(self, record: LogRecord) -> None:
        """
        Proses catatan log dan cetak ke konsol dengan format Rich.
        """
        
        # Mendapatkan format waktu dari formatter
        time_format = None
        if self.formatter:
            time_format = getattr(self.formatter, 'datefmt', None) or "%X"

        log_time = datetime.datetime.fromtimestamp(record.created)
        level = self.get_level_text(record)
        message = self.format(record)
        
        # PENTING: Hapus argumen 'logger_name' karena sudah tidak didukung di rich versi baru.
        self.console.print(
            self._log_render(
                self.console,
                [Text(message)],
                log_time=log_time,
                time_format=time_format,
                level=level,
                path=pathlib.Path(record.pathname).name,
                line_no=record.lineno,
                link_path=record.pathname if self.enable_link_path else None,
            ),
            soft_wrap=True,
        )

def setup_logging(level: int) -> None:
    """
    Inisialisasi sistem logging dengan handler konsol Rich kustom dan handler file.
    """

    system("cls" if name == "nt" else "clear")

    rich_console = Console(tab_size=4)
    rich_console.push_theme(
        Theme(
            {
                "log.time": Style(dim=True),
                "logging.level.warning": Style(color="yellow", bold=True),
                "logging.level.error": Style(color="red", bold=True),
                "logging.level.critical": Style(color="white", bgcolor="red", bold=True),
                "repr.number": Style(color="cyan"),
                "repr.url": Style(underline=True, italic=True, bold=False, color="cyan"),
            }
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    logging.captureWarnings(True)

    console_handler = CustomRichHandler(console=rich_console, rich_tracebacks=True)
    root_logger.addHandler(console_handler)

    for module in ("discord", "httpx", "pylast", "websockets.server"):
        logger = logging.getLogger(module)
        logger.setLevel(logging.WARNING)

    log_file_path = pathlib.Path("utils/logs/discord.log")
    log_file_path.parent.mkdir(parents=True, exist_ok=True) # Pastikan folder ada

    file_handler = handlers.RotatingFileHandler(
        log_file_path,
        encoding="utf-8",
        mode="a",
        maxBytes=32 * 1024 * 1024,
        backupCount=3,
    )
    file_formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style='{',
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)