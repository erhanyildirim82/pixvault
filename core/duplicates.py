"""
duplicates.py — Duplikat tespit modülü.
Önce boyut, sonra MD5 hash karşılaştırması yapar.
"""

import hashlib
from pathlib import Path
from collections import defaultdict

from core.scanner import FileInfo


def compute_md5(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def detect_duplicates(
    files: list[FileInfo],
    progress_callback=None,
    log_callback=None,
) -> list[FileInfo]:
    """
    files listesini in-place günceller:
    - is_duplicate = True
    - duplicate_of = orijinal dosyanın Path'i
    - md5 alanı doldurulur (duplikat adaylarında)
    Güncellenmiş listeyi döndürür.
    """

    # 1. Boyuta göre grupla
    by_size: dict[int, list[FileInfo]] = defaultdict(list)
    for fi in files:
        if fi.file_type != 'unknown':
            by_size[fi.size].append(fi)

    candidates = [group for group in by_size.values() if len(group) > 1]
    total_candidates = sum(len(g) for g in candidates)
    processed = 0

    # 2. Aynı boyutlular için MD5 hesapla
    for group in candidates:
        by_hash: dict[str, FileInfo] = {}
        for fi in group:
            if fi.md5 is None:
                try:
                    fi.md5 = compute_md5(fi.path)
                except Exception as e:
                    if log_callback:
                        log_callback('warn', f'MD5 hesaplanamadı {fi.path.name}: {e}')
                    processed += 1
                    continue

            if fi.md5 in by_hash:
                fi.is_duplicate = True
                fi.duplicate_of = by_hash[fi.md5].path
                if log_callback:
                    log_callback(
                        'duplicate',
                        f'{fi.path.name} → Tekrar ({by_hash[fi.md5].path.name} kopyası)',
                    )
            else:
                by_hash[fi.md5] = fi

            processed += 1
            if progress_callback:
                progress_callback(processed, total_candidates)

    return files
