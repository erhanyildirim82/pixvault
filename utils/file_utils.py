"""
file_utils.py — Yardımcı dosya fonksiyonları.
"""

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """
    PyInstaller ile paketlenmiş veya normal çalışmada
    images/ gibi kaynaklara doğru yolu döndürür.
    """
    if hasattr(sys, '_MEIPASS'):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent
    return base / relative


def safe_delete_files(paths: list[Path], log_callback=None) -> tuple[int, list[str]]:
    """
    Verilen dosyaları siler. Başarılı sayısı ve hata listesi döndürür.
    """
    success = 0
    errors = []
    for p in paths:
        try:
            p.unlink()
            success += 1
            if log_callback:
                log_callback('info', f'Silindi: {p}')
        except Exception as e:
            msg = f'Silinemedi {p.name}: {e}'
            errors.append(msg)
            if log_callback:
                log_callback('error', msg)
    return success, errors


def count_files_in_dir(directory: Path) -> int:
    try:
        return sum(1 for p in directory.rglob('*') if p.is_file())
    except Exception:
        return 0


def _generate_check_icon(path: Path, color: str = '#FFFFFF') -> None:
    """QPainter ile beyaz tik işareti PNG'si çizer."""
    from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
    from PyQt6.QtCore import Qt, QPointF

    pm = QPixmap(16, 16)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color), 2.2)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(QPointF(2.5, 8.0), QPointF(5.5, 11.5))
    painter.drawLine(QPointF(5.5, 11.5), QPointF(13.0, 4.0))
    painter.end()
    pm.save(str(path))


def ensure_ui_assets() -> dict:
    """
    QSS'de kullanılacak tik işareti PNG'lerini oluşturur.
    QApplication başlatıldıktan SONRA çağrılmalıdır.
    Döndürür: {'check_white': '/path/check_white.png'}
    """
    assets_dir = Path.home() / '.pixvault' / 'assets'
    assets_dir.mkdir(parents=True, exist_ok=True)

    check_white = assets_dir / 'check_white.png'
    if not check_white.exists():
        _generate_check_icon(check_white, '#FFFFFF')

    return {
        'check_white': str(check_white).replace('\\', '/'),
    }
