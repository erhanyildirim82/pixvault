"""
event_dialog.py — Etkinlik adı dialog'u.
"""

from datetime import date

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt

from core.event_group import EventGroup, TURKISH_MONTHS
from utils.i18n import t


class EventDialog(QDialog):

    def __init__(self, selected_dates: list[date], total_files: int, parent=None):
        super().__init__(parent)
        self.selected_dates = sorted(selected_dates)
        self.total_files    = total_files
        self.event_group: EventGroup | None = None

        self.setWindowTitle(t('event_dlg_title'))
        self.setFixedWidth(390)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_days = QLabel(f'{t("event_days")} {self._format_dates()}')
        lbl_days.setStyleSheet('color: #555555;')
        layout.addWidget(lbl_days)

        lbl_count = QLabel(f'{t("event_file_count")} {self.total_files}')
        lbl_count.setStyleSheet('color: #555555;')
        layout.addWidget(lbl_count)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet('color: #E0E0E0;')
        layout.addWidget(sep)

        layout.addWidget(QLabel(t('event_name_lbl')))

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(t('event_placeholder'))
        self.name_edit.textChanged.connect(self._update_preview)
        layout.addWidget(self.name_edit)

        lbl_folder_title = QLabel(t('event_folder_lbl'))
        lbl_folder_title.setStyleSheet('color: #888888; font-size: 9pt;')
        layout.addWidget(lbl_folder_title)

        self.lbl_preview = QLabel('')
        self.lbl_preview.setStyleSheet(
            'background: #EBF3FB; border-radius: 4px; padding: 6px 10px; '
            'font-family: Consolas, monospace; color: #005A9E;'
        )
        self.lbl_preview.setWordWrap(True)
        layout.addWidget(self.lbl_preview)

        layout.addSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton(t('cancel'))
        self.btn_cancel.setObjectName('secondaryBtn')
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_ok = QPushButton(t('ok'))
        self.btn_ok.setFixedWidth(90)
        self.btn_ok.setEnabled(False)
        self.btn_ok.clicked.connect(self._accept)
        btn_row.addWidget(self.btn_ok)

        layout.addLayout(btn_row)
        self._update_preview()

    def _format_dates(self) -> str:
        if not self.selected_dates:
            return ''
        if all(d.month == self.selected_dates[0].month for d in self.selected_dates):
            days = '-'.join(str(d.day) for d in self.selected_dates)
            return f'{days} {TURKISH_MONTHS[self.selected_dates[0].month]}'
        return ', '.join(f'{d.day} {TURKISH_MONTHS[d.month]}' for d in self.selected_dates)

    def _update_preview(self):
        name = self.name_edit.text().strip()
        if name:
            eg = EventGroup(name=name, dates=self.selected_dates)
            self.lbl_preview.setText(eg.folder_name)
            self.btn_ok.setEnabled(True)
        else:
            self.lbl_preview.setText('')
            self.btn_ok.setEnabled(False)

    def _accept(self):
        name = self.name_edit.text().strip()
        if name:
            self.event_group = EventGroup(name=name, dates=self.selected_dates)
            self.accept()
