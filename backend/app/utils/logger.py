"""
Logger — console + optional file logging.
File logging is skipped on read-only filesystems (e.g. Vercel serverless).
"""

import os
import sys
import logging
from datetime import datetime

# Detect serverless environment (Vercel sets VERCEL=1)
IS_SERVERLESS = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')


def _ensure_utf8_stdout():
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def setup_logger(name: str = 'swarmmind', level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    # File handler — skip on serverless (read-only filesystem)
    if not IS_SERVERLESS:
        try:
            from logging.handlers import RotatingFileHandler
            os.makedirs(LOG_DIR, exist_ok=True)
            log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
            file_handler = RotatingFileHandler(
                os.path.join(LOG_DIR, log_filename),
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except OSError:
            pass  # read-only filesystem, skip file logging

    # Console handler
    _ensure_utf8_stdout()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = 'swarmmind') -> logging.Logger:
    """Get a logger by name, creating it if needed."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


logger = setup_logger()

