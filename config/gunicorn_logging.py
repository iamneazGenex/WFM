import os
from logging.handlers import TimedRotatingFileHandler

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
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "filename": os.path.join(log_directory, "app.log"),  # Base filename
            "when": "midnight",  # Rotate at midnight
            "interval": 1,  # Rotate every day
            "backupCount": 0,  # Keep all logs indefinitely
            "encoding": "utf-8",
            "utc": True,  # Use UTC time for rotation
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
