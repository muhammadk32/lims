"""
Central logging setup for LabMS.
Writes to console (INFO) and rotating file logs/app.log (INFO+).
Errors also go to logs/errors.log.
"""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configure app logging. Call once inside create_app()."""
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # ---------- Root logger ----------
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Remove existing handlers to prevent duplicates on reload
    for h in list(root.handlers):
        root.removeHandler(h)

    # ---------- Format ----------
    fmt = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # ---------- Console ----------
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)

    # ---------- Rotating file: all logs ----------
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=5,
        encoding='utf-8',
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # ---------- Rotating file: errors only ----------
    err_handler = RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
    )
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(fmt)
    root.addHandler(err_handler)

    # Silence noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info('📝 Logging initialized (logs/app.log)')