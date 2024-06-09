import multiprocessing
from config.gunicorn_logging import configure_logging

# Call the configure_logging function to set up logging
configure_logging()

# Define Gunicorn configuration variables
bind = "unix:/run/gunicorn.sock"
workers = multiprocessing.cpu_count() * 2 + 1
limit_request_line = 0
timeout = 3600
graceful_timeout = 3600
keepalive = 3600
accesslog = "-"  # Redirect Gunicorn access logs to stdout
errorlog = "-"  # Redirect Gunicorn error logs to stdout
loglevel = "debug"
worker_class = "eventlet"
# Specify the working directory
WorkingDirectory = "/home/wfmuser/WFM"
