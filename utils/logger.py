"""
logger.py — Log dosyası yönetimi.
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_file_logger(log_dir: Path = None) -> logging.Logger:
    """
    Günlük log dosyası oluşturur: pixvault_log_YYYY-MM-DD.txt
    log_dir verilmezse kullanıcının masaüstüne yazar.
    """
    if log_dir is None:
        log_dir = Path.home() / 'Desktop'
    log_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file = log_dir / f'pixvault_log_{date_str}.txt'

    logger = logging.getLogger('pixvault')
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(str(log_file), encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger('pixvault')
