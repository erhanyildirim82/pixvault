"""
main.py — PixVault uygulama giriş noktası.
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter, QBrush

from utils import settings_manager as sm
from utils.i18n import set_language
from ui.styles import get_stylesheet
from ui.main_window import MainWindow
from utils.file_utils import resource_path, ensure_ui_assets


def create_fallback_splash(dark: bool = False) -> QPixmap:
    bg  = QColor('#1E1E1E') if dark else QColor('#FFFFFF')
    fg  = QColor('#4DB8FF') if dark else QColor('#0078D4')
    sub = QColor('#AAAAAA') if dark else QColor('#888888')

    pm = QPixmap(480, 160)
    pm.fill(bg)

    painter = QPainter(pm)
    font_title = QFont('Segoe UI', 34, QFont.Weight.Light)
    painter.setFont(font_title)
    painter.setPen(fg)
    painter.drawText(pm.rect().adjusted(0, -20, 0, 0), Qt.AlignmentFlag.AlignCenter, 'PixVault')

    font_sub = QFont('Segoe UI', 11)
    painter.setFont(font_sub)
    painter.setPen(sub)
    painter.drawText(
        pm.rect().adjusted(0, 55, 0, 0),
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        'Fotoğraf & Video Arşivleme',
    )
    painter.end()
    return pm


def main():
    # Ayarları yükle
    settings = sm.load_all()
    set_language(settings.get('language', 'tr'))
    theme = sm.resolve_theme()

    app = QApplication(sys.argv)
    app.setApplicationName('PixVault')
    app.setOrganizationName('PixVault')

    # QApplication başladıktan sonra tik ikonunu oluştur
    assets = ensure_ui_assets()
    app.setStyleSheet(get_stylesheet(theme, assets))

    # Splash screen
    logo_path = resource_path('images/logo.png')
    if logo_path.exists():
        pixmap = QPixmap(str(logo_path))
    else:
        pixmap = create_fallback_splash(dark=(theme == 'dark'))

    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
    splash.show()
    app.processEvents()

    window = MainWindow()

    def show_main():
        splash.finish(window)
        window.show()

    # MediaInfo kontrolü — video metadata için gerekli
    from core.scanner import MEDIAINFO_AVAILABLE
    if not MEDIAINFO_AVAILABLE:
        def _warn_mediainfo():
            from PyQt6.QtWidgets import QMessageBox
            dlg = QMessageBox(window)
            dlg.setWindowTitle('MediaInfo Bulunamadı')
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.setText(
                '<b>MediaInfo kütüphanesi yüklenemedi.</b><br><br>'
                'Video dosyalarının tarih bilgisi okunamayacak; '
                'bu dosyalar <i>Tarihsiz</i> klasörüne taşınacaktır.<br><br>'
                'Fotoğraflar etkilenmez.<br><br>'
                '<b>Çözüm:</b> Aşağıdaki adresten MediaInfo uygulamasını kurun, '
                'ardından PixVault\'u yeniden başlatın.<br>'
                '<a href="https://mediaarea.net/en/MediaInfo/Download/Windows">'
                'mediaarea.net → Download → Windows</a>'
            )
            dlg.setTextFormat(Qt.TextFormat.RichText)
            dlg.exec()
        QTimer.singleShot(1800, _warn_mediainfo)

    QTimer.singleShot(1500, show_main)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
