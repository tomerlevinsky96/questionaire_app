

# gunicorn_config.py
workers = 3
threads = 2
worker_class = 'gthread'
timeout = 120
keepalive = 65
max_requests = 1000
max_requests_jitter = 50