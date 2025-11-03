"""
Logging configuration and utilities.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g
import time


def setup_logging(app: Flask):
    """
    Configure application logging.
    
    Args:
        app: Flask application instance
    """
    # Create logs directory
    log_file = Path(app.config['LOG_FILE'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Set log level
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    app.logger.setLevel(log_level)
    
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)
    
    # Log startup
    app.logger.info(f"Application started in {app.config['FLASK_ENV']} mode")
    app.logger.info(f"Logging to: {log_file}")


def log_request():
    """Log incoming request details"""
    g.start_time = time.time()


def log_response(response):
    """
    Log response details.
    
    Args:
        response: Flask response object
        
    Returns:
        Modified response object
    """
    from flask import current_app
    
    # Calculate response time
    response_time = (time.time() - g.get('start_time', time.time())) * 1000
    
    # Log request/response
    current_app.logger.info(
        f"{request.method} {request.path} - "
        f"Status: {response.status_code} - "
        f"Time: {response_time:.2f}ms - "
        f"IP: {request.remote_addr}"
    )
    
    # Add response time header
    response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
    
    return response


def log_error(error):
    """
    Log error details.
    
    Args:
        error: Exception object
    """
    from flask import current_app
    
    current_app.logger.error(
        f"Error: {str(error)} - "
        f"Path: {request.path} - "
        f"Method: {request.method} - "
        f"IP: {request.remote_addr}",
        exc_info=True
    )


class RequestLogger:
    """Context manager for logging request details"""
    
    def __init__(self, operation: str):
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        from flask import current_app
        self.start_time = time.time()
        current_app.logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        from flask import current_app
        elapsed = (time.time() - self.start_time) * 1000
        
        if exc_type:
            current_app.logger.error(
                f"Failed: {self.operation} - {elapsed:.2f}ms - Error: {exc_val}"
            )
        else:
            current_app.logger.debug(f"Completed: {self.operation} - {elapsed:.2f}ms")
        
        return False  # Don't suppress exceptions
