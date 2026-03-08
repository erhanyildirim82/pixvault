"""
settings_dialog.py — Tema, dil ve hakkında ayarları.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QFrame, QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from utils.i18n import t
from utils import settings_manager as sm

APP_VERSION = 'V1.0.0'
APP_NAME    = 'PixVault'
GITHUB_URL  = 'https://github.com/erhanyildirim82'


class SettingsDialog(QDialog):
    """
    Ayarlar penceresi.
    Sinyal: theme_changed(str), language_changed(str)
    """

    theme_changed    = pyqtSignal(str)
    language_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('settings_title'))
        self.setFixedWidth(360)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Tema ---
        layout.addWidget(self._section_label(t('theme_section')))

        theme_box = QGroupBox()
        theme_box.setFlat(True)
        theme_layout = QHBoxLayout(theme_box)
        theme_layout.setSpacing(8)

        current_theme = sm.get('theme') or 'light'
        self._theme_group = QButtonGroup(self)

        themes = [
            ('light', t('theme_light')),
            ('dark',  t('theme_dark')),
            ('auto',  t('theme_auto')),
        ]
        for value, label in themes:
            rb = QRadioButton(label)
            rb.setChecked(value == current_theme)
            rb.toggled.connect(lambda checked, v=value: self._on_theme(v, checked))
            self._theme_group.addButton(rb)
            theme_layout.addWidget(rb)

        layout.addWidget(theme_box)

        # --- Dil ---
        layout.addWidget(self._section_label(t('lang_section')))

        lang_box = QGroupBox()
        lang_box.setFlat(True)
        lang_layout = QHBoxLayout(lang_box)
        lang_layout.setSpacing(8)

        current_lang = sm.get('language') or 'tr'
        self._lang_group = QButtonGroup(self)

        rb_tr = QRadioButton('Türkçe')
        rb_en = QRadioButton('English')
        rb_tr.setChecked(current_lang == 'tr')
        rb_en.setChecked(current_lang == 'en')

        rb_tr.toggled.connect(lambda checked: self._on_lang('tr', checked))
        rb_en.toggled.connect(lambda checked: self._on_lang('en', checked))

        self._lang_group.addButton(rb_tr)
        self._lang_group.addButton(rb_en)
        lang_layout.addWidget(rb_tr)
        lang_layout.addWidget(rb_en)
        layout.addWidget(lang_box)

        note = QLabel(t('restart_note'))
        note.setObjectName('fieldLabel')
        note.setStyleSheet('QLabel { font-size: 8.5pt; }')
        note.setWordWrap(True)
        layout.addWidget(note)

        # --- Hakkında ---
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        layout.addWidget(self._section_label(t('about_section')))

        about_box = QGroupBox()
        about_box.setFlat(True)
        about_layout = QVBoxLayout(about_box)
        about_layout.setSpacing(4)

        lbl_name = QLabel(APP_NAME)
        f = QFont('Segoe UI', 16, QFont.Weight.Light)
        lbl_name.setFont(f)
        lbl_name.setObjectName('statsValue')
        about_layout.addWidget(lbl_name)

        ver_row = QHBoxLayout()
        ver_row.setSpacing(12)
        lbl_ver = QLabel(APP_VERSION)
        lbl_ver.setObjectName('fieldLabel')
        ver_row.addWidget(lbl_ver)
        lbl_author = QLabel(f'<a href="{GITHUB_URL}" style="color:#0078D4; text-decoration:none;">Erhan/Dev</a>')
        lbl_author.setOpenExternalLinks(True)
        lbl_author.setObjectName('fieldLabel')
        ver_row.addWidget(lbl_author)
        ver_row.addStretch()
        about_layout.addLayout(ver_row)

        lbl_desc = QLabel(t('about_desc'))
        lbl_desc.setWordWrap(True)
        lbl_desc.setObjectName('fieldLabel')
        lbl_desc.setStyleSheet('QLabel { margin-top: 6px; font-size: 9pt; }')
        about_layout.addWidget(lbl_desc)

        layout.addWidget(about_box)

        # --- Kapat ---
        layout.addSpacing(4)
        btn_close = QPushButton(t('close'))
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(btn_close)
        layout.addLayout(h)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName('fieldLabel')
        lbl.setStyleSheet('QLabel#fieldLabel { font-size: 9.5pt; }')
        return lbl

    def _on_theme(self, value: str, checked: bool):
        if checked:
            sm.set_value('theme', value)
            self.theme_changed.emit(value)

    def _on_lang(self, value: str, checked: bool):
        if checked:
            sm.set_value('language', value)
            self.language_changed.emit(value)
