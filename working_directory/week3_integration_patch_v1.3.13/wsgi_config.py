"""
WSGI Configuration for Production Regime Dashboard
Gunicorn production server configuration

Usage:
    gunicorn -c wsgi_config.py regime_dashboard_production:app

Author: Trading System v1.3.13 - PRODUCTION EDITION
Date: January 6, 2026
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5002"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = '/var/log/regime-dashboard/access.log'
errorlog = '/var/log/regime-dashboard/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'regime-dashboard'

# Server mechanics
daemon = False
pidfile = '/var/run/regime-dashboard.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

def post_fork(server, worker):
    """Post-fork hook"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_fork(server, worker):
    """Pre-fork hook"""
    pass

def pre_exec(server):
    """Pre-exec hook"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Server ready hook"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Worker interrupted"""
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """Worker aborted"""
    worker.log.info("worker received SIGABRT signal")
