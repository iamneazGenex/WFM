import multiprocessing
from config.gunicorn_logging import configure_logging

# Call the configure_logging function to set up logging
configure_logging()

# Define Gunicorn configuration variables

# bind = "unix:/run/gunicorn.sock"
# workers = multiprocessing.cpu_count() * 2 + 1
# limit_request_line = 0
# timeout = 3600
# graceful_timeout = 3600
# keepalive = 3600
# accesslog = "-"  # Redirect Gunicorn access logs to stdout
# errorlog = "-"  # Redirect Gunicorn error logs to stdout
# loglevel = "debug"
# worker_class = "gevent"
# max_requests = 1000  # Restart worker after processing 1000 requests
# # Specify the working directory
# WorkingDirectory = "/home/wfmuser/WFM"

bind = "unix:/run/gunicorn.sock"
workers = multiprocessing.cpu_count() + 1
limit_request_line = 0
timeout = 3600 * 2  # Reduce timeout to a more reasonable value
graceful_timeout = 3600 * 2  # Reduce graceful timeout
keepalive = 3600 * 2  # Reduce keepalive to free up idle connections
accesslog = "-"  # Redirect Gunicorn access logs to stdout
errorlog = "-"  # Redirect Gunicorn error logs to stdout
loglevel = "debug"
worker_class = "gevent"
max_requests = 1000  # Restart worker after processing 1000 requests
max_requests_jitter = 100  # Add jitter to max_requests to spread out restarts
# Specify the working directory
working_directory = "/home/wfmuser/WFM"
