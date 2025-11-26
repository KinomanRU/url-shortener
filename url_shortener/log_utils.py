import logging
from config import config


def init_logging():
    logging.basicConfig(
        level=logging.DEBUG if config.getboolean("Debug", "Debug") else logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        filename=(
            config.get("Logging", "Log_File")
            if config.getboolean("Logging", "Log_To_File")
            else None
        ),
        encoding="utf-8",
    )
