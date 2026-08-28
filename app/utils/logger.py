import logging
from logging.handlers import RotatingFileHandler


file_handler= RotatingFileHandler(
    "app.log",
    maxBytes=10_000_000,
    backupCount=5,
    encoding="utf-8"
)

console_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s |%(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        file_handler,
        console_handler
    ],
)
logging.getLogger("watchfiles").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
