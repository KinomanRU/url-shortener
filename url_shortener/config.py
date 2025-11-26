from pathlib import Path
from configparser import ConfigParser

BASE_DIR = Path(__file__).resolve().parent

FILE = "settings.ini"
DEV_FILE = "settings_dev.ini"

FILES = [
    BASE_DIR / FILE,
    BASE_DIR.parent / FILE,
]
DEV_FILES = [
    BASE_DIR / DEV_FILE,
    BASE_DIR.parent / DEV_FILE,
]

config = ConfigParser()

if not config.read(DEV_FILES):
    if not config.read(FILES):
        raise FileNotFoundError
