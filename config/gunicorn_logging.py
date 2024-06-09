import os
from logging.handlers import TimedRotatingFileHandler
from concurrent_log_handler import ConcurrentRotatingFileHandler

# Define the log directory and ensure it exists
log_directory = "/home/wfmuser/WFM/logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

loglevel = "debug"  # Set your desired log level

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "formatter": "default",
            "filename": os.path.join(log_directory, "app.log"),  # Base filename
            "maxBytes": 100 * 1024 * 1024,  # Rotate log files at 10MB
            "backupCount": 20,  # Keep all log files
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {
            "level": loglevel.upper(),
            "handlers": [
                "console",
                "file",
            ],
        },
    },
}


def configure_logging():
    import logging.config

    logging.config.dictConfig(LOGGING)
