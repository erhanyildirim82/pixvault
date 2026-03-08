"""
main_window.py — PixVault ana penceresi.
"""

from pathlib import Path
from datetime import date
from collections import defaultdict

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QButtonGroup,
    QCheckBox, QTreeWidget, QTreeWidgetItem, QTextEdit,
    QProgressBar, QFrame, QFileDialog, QMessageBox, QDialog,
    QScrollArea, QApplication, QStackedWidget, QStyle,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPointF
from PyQt6.QtGui import QColor, QTextCursor, QIcon, QPixmap, QPainter, QBrush, QPolygonF

from ui.styles import LOG_COLORS, LOG_ICONS, get_stylesheet
from ui.event_dialog import EventDialog
from ui.settings_dialog import SettingsDialog
from core.scanner import Scanner, FileInfo
from core.duplicates import detect_duplicates
from core.organizer import Organizer
from core.event_group import EventGroup, TURKISH_MONTHS
from utils.logger import setup_file_logger, get_logger
from utils.file_utils import resource_path, safe_delete_files, count_files_in_dir
from utils.i18n import t, set_language, get_language
from utils import settings_manager as sm


# ---------------------------------------------------------------------------
# Worker — tarama + duplikat
# ---------------------------------------------------------------------------

class ScanWorker(QThread):
    progress = pyqtSignal(int, int)
    log_msg  = pyqtSignal(str, str)
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, source_dir: Path):
        super().__init__()
        self.source_dir = source_dir
        self._scanner: Scanner | None = None

    def cancel(self):
        if self._scanner:
            self._scanner.cancel()

    def run(self):
        try:
            self._scanner = Scanner(
                progress_callback=lambda c, total: self.progress.emit(c, total),
                log_callback=lambda lvl, msg: self.log_msg.emit(lvl, msg),
            )
            files = self._scanner.scan(self.source_dir)
            detect_duplicates(files, log_callback=lambda lvl, msg: self.log_msg.emit(lvl, msg))
            self.finished.emit(files)
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------------------------------------------------------
# Worker — düzenleme
# ---------------------------------------------------------------------------

class OrganizeWorker(QThread):
    progress = pyqtSignal(int, int)
    log_msg  = pyqtSignal(str, str)
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, files, target_dir, mode, separate_types, event_groups, dry_run=False):
        super().__init__()
        self.files = files
        self.target_dir = target_dir
        self.mode = mode
        self.separate_types = separate_types
        self.event_groups = event_groups
        self.dry_run = dry_run
        self._organizer: Organizer | None = None

    def cancel(self):
        if self._organizer:
            self._organizer.cancel()

    def run(self):
        try:
            self._organizer = Organizer(
                target_dir=self.target_dir,
                mode=self.mode,
                separate_types=self.separate_types,
                event_groups=self.event_groups,
                progress_callback=lambda c, total: self.progress.emit(c, total),
                log_callback=lambda lvl, msg: self.log_msg.emit(lvl, msg),
            )
            if self.dry_run:
                plan = self._organizer.dry_run(self.files)
                result = {'dry_run': True, 'plan': plan, 'success': len(plan), 'skipped': 0, 'errors': []}
            else:
                result = self._organizer.run(self.files)
                result['dry_run'] = False
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------------------------------------------------------
# Ana pencere
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('PixVault')
        self.setMinimumSize(1100, 700)
        self.resize(1280, 780)

        icon_path = resource_path('images/icon.ico')
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Durum
        self._scanned_files: list[FileInfo] = []
        self._event_groups:  list[EventGroup] = []
        self._scan_worker:   ScanWorker | None = None
        self._org_worker:    OrganizeWorker | None = None
        self._pending_move:  bool = False   # True → kopyalama bitti, silme onayı bekliyor

        self._build_ui()
        self._retranslate()
        self._apply_icons()
        self._set_initial_state()

    # -----------------------------------------------------------------------
    # Arayüz oluşturma
    # -----------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._build_mode_bar())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(6, 6, 6, 4)
        body_layout.setSpacing(5)
        body_layout.addWidget(self._build_main_splitter())
        root.addWidget(body, stretch=1)

        root.addWidget(self._build_log_area())
        root.addWidget(self._build_bottom_bar())

    # --- Mod çubuğu ---

    def _build_mode_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName('modeBar')
        bar.setFixedHeight(46)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(0)

        self.lbl_mode = QLabel()
        self.lbl_mode.setStyleSheet('font-weight: 600; margin-right: 8px;')
        layout.addWidget(self.lbl_mode)

        self.btn_mode_new = QPushButton()
        self.btn_mode_new.setObjectName('segBtnLeft')
        self.btn_mode_new.setCheckable(True)
        self.btn_mode_new.setChecked(True)
        self.btn_mode_new.setFixedHeight(30)

        self.btn_mode_add = QPushButton()
        self.btn_mode_add.setObjectName('segBtnRight')
        self.btn_mode_add.setCheckable(True)
        self.btn_mode_add.setFixedHeight(30)

        self._mode_group = QButtonGroup(self)
        self._mode_group.setExclusive(True)
        self._mode_group.addButton(self.btn_mode_new, 0)
        self._mode_group.addButton(self.btn_mode_add, 1)
        self._mode_group.buttonClicked.connect(self._on_mode_changed)

        layout.addWidget(self.btn_mode_new)
        layout.addWidget(self.btn_mode_add)
        layout.addStretch()

        self.btn_settings = QPushButton()
        self.btn_settings.setObjectName('secondaryBtn')
        self.btn_settings.setFixedHeight(30)
        self.btn_settings.clicked.connect(self._open_settings)
        layout.addWidget(self.btn_settings)

        return bar

    # --- Panel başlık yardımcısı ---

    def _panel_header(self, i18n_key: str) -> QWidget:
        """Nikon Transfer 2 tarzı bölüm başlığı (mavi sol şerit + büyük harf başlık)."""
        header = QWidget()
        header.setObjectName('panelHeader')
        header.setFixedHeight(28)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 8, 0)
        lbl = QLabel(t(i18n_key))
        lbl.setObjectName('panelHeaderLabel')
        layout.addWidget(lbl)
        layout.addStretch()
        # retranslate için sakla
        self._panel_header_labels = getattr(self, '_panel_header_labels', {})
        self._panel_header_labels[i18n_key] = lbl
        return header

    # --- Ana splitter ---

    def _build_main_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        splitter.setStyleSheet('QSplitter::handle { background: #888888; }')

        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_center_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([240, 620, 220])
        return splitter

    # --- Sol panel ---

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName('leftPanel')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._panel_header('panel_folders'))

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(8)

        self.lbl_source = QLabel()
        self.lbl_source.setObjectName('fieldLabel')
        cl.addWidget(self.lbl_source)

        src_row = QHBoxLayout()
        src_row.setSpacing(4)
        self.edit_source = QLineEdit()
        self.edit_source.setReadOnly(True)
        src_row.addWidget(self.edit_source)
        self.btn_source = QPushButton()
        self.btn_source.setMinimumWidth(52)
        self.btn_source.setFixedHeight(26)
        self.btn_source.clicked.connect(self._pick_source)
        src_row.addWidget(self.btn_source)
        cl.addLayout(src_row)

        cl.addSpacing(4)

        self.lbl_target = QLabel()
        self.lbl_target.setObjectName('fieldLabel')
        cl.addWidget(self.lbl_target)

        dst_row = QHBoxLayout()
        dst_row.setSpacing(4)
        self.edit_target = QLineEdit()
        self.edit_target.setReadOnly(True)
        dst_row.addWidget(self.edit_target)
        self.btn_target = QPushButton()
        self.btn_target.setMinimumWidth(52)
        self.btn_target.setFixedHeight(26)
        self.btn_target.clicked.connect(self._pick_target)
        dst_row.addWidget(self.btn_target)
        cl.addLayout(dst_row)

        cl.addStretch()

        self.btn_scan = QPushButton()
        self.btn_scan.setFixedHeight(34)
        self.btn_scan.clicked.connect(self._start_scan)
        cl.addWidget(self.btn_scan)

        layout.addWidget(content, stretch=1)
        return panel

    # --- Orta panel ---

    def _build_center_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName('centerPanel')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._panel_header('panel_scan'))

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(10, 10, 10, 10)
        cl.setSpacing(8)

        # --- Tree / Empty state yığını ---
        self._tree_stack = QStackedWidget()

        # Sayfa 0: Boş durum
        empty_widget = QWidget()
        el = QVBoxLayout(empty_widget)
        el.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_empty = QLabel()
        self._lbl_empty.setObjectName('emptyStateLabel')
        self._lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_empty.setWordWrap(True)
        el.addWidget(self._lbl_empty)

        # Sayfa 1: Ağaç görünümü
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree.itemChanged.connect(self._on_tree_item_changed)

        self._tree_stack.addWidget(empty_widget)   # index 0
        self._tree_stack.addWidget(self.tree)      # index 1
        self._tree_stack.setCurrentIndex(0)

        cl.addWidget(self._tree_stack, stretch=1)

        self.btn_group_event = QPushButton()
        self.btn_group_event.setObjectName('secondaryBtn')
        self.btn_group_event.setEnabled(False)
        self.btn_group_event.setFixedHeight(28)
        self.btn_group_event.clicked.connect(self._group_as_event)
        cl.addWidget(self.btn_group_event)

        self.lbl_events = QLabel()
        self.lbl_events.setObjectName('fieldLabel')
        cl.addWidget(self.lbl_events)

        self._event_list_widget = QWidget()
        self._event_list_layout = QVBoxLayout(self._event_list_widget)
        self._event_list_layout.setContentsMargins(0, 0, 0, 0)
        self._event_list_layout.setSpacing(3)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._event_list_widget)
        scroll.setMaximumHeight(100)
        scroll.setStyleSheet('QScrollArea { border: none; }')
        cl.addWidget(scroll)

        layout.addWidget(content, stretch=1)
        return panel

    # --- Sağ panel ---

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName('rightPanel')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._panel_header('panel_options'))

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.setSpacing(8)

        self.lbl_operation = QLabel()
        self.lbl_operation.setObjectName('fieldLabel')
        cl.addWidget(self.lbl_operation)

        self.btn_op_copy = QPushButton()
        self.btn_op_copy.setObjectName('segBtnLeft')
        self.btn_op_copy.setCheckable(True)
        self.btn_op_copy.setChecked(True)
        self.btn_op_copy.setFixedHeight(28)

        self.btn_op_move = QPushButton()
        self.btn_op_move.setObjectName('segBtnRight')
        self.btn_op_move.setCheckable(True)
        self.btn_op_move.setFixedHeight(28)

        op_group = QButtonGroup(self)
        op_group.setExclusive(True)
        op_group.addButton(self.btn_op_copy, 0)
        op_group.addButton(self.btn_op_move, 1)

        op_row = QHBoxLayout()
        op_row.setSpacing(0)
        op_row.addWidget(self.btn_op_copy)
        op_row.addWidget(self.btn_op_move)
        op_row.addStretch()
        cl.addLayout(op_row)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet('color: #444444; margin: 4px 0;')
        cl.addWidget(sep1)

        self.cb_separate = QCheckBox()
        self.cb_separate.setChecked(True)
        cl.addWidget(self.cb_separate)

        self.cb_duplicates = QCheckBox()
        self.cb_duplicates.setChecked(True)
        cl.addWidget(self.cb_duplicates)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet('color: #444444; margin: 4px 0;')
        cl.addWidget(sep2)

        self.lbl_statistics = QLabel()
        self.lbl_statistics.setObjectName('fieldLabel')
        cl.addWidget(self.lbl_statistics)

        self.lbl_total   = self._stat_row(cl, 'total')
        self.lbl_photos  = self._stat_row(cl, 'photos')
        self.lbl_videos  = self._stat_row(cl, 'videos')
        self.lbl_dupes   = self._stat_row(cl, 'dupes')
        self.lbl_no_date = self._stat_row(cl, 'no_date')
        self.lbl_unknown = self._stat_row(cl, 'other')

        cl.addStretch()
        layout.addWidget(content, stretch=1)
        return panel

    def _stat_row(self, parent_layout, key: str) -> QLabel:
        row = QHBoxLayout()
        row.setSpacing(4)
        lbl = QLabel()
        lbl.setObjectName('fieldLabel')
        val = QLabel('—')
        val.setObjectName('statsValue')
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        parent_layout.addLayout(row)
        self._stat_labels = getattr(self, '_stat_labels', {})
        self._stat_labels[key] = lbl
        return val

    # --- Log alanı ---

    def _build_log_area(self) -> QWidget:
        self.log_text = QTextEdit()
        self.log_text.setObjectName('logArea')
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(96)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        return self.log_text

    # --- Alt çubuk ---

    def _build_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName('bottomBar')
        bar.setFixedHeight(46)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar, stretch=1)

        self.lbl_progress = QLabel()
        self.lbl_progress.setStyleSheet('color: #888888; font-size: 9pt; min-width: 140px;')
        layout.addWidget(self.lbl_progress)

        layout.addSpacing(6)

        self.btn_preview = QPushButton()
        self.btn_preview.setObjectName('secondaryBtn')
        self.btn_preview.setFixedHeight(30)
        self.btn_preview.setMinimumWidth(90)
        self.btn_preview.setEnabled(False)
        self.btn_preview.clicked.connect(self._start_preview)
        layout.addWidget(self.btn_preview)

        self.btn_start = QPushButton()
        self.btn_start.setFixedHeight(30)
        self.btn_start.setMinimumWidth(100)
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self._start_organize)
        layout.addWidget(self.btn_start)

        self.btn_cancel = QPushButton()
        self.btn_cancel.setObjectName('secondaryBtn')
        self.btn_cancel.setFixedHeight(30)
        self.btn_cancel.setMinimumWidth(80)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_operation)
        layout.addWidget(self.btn_cancel)

        return bar

    # -----------------------------------------------------------------------
    # i18n — tüm widget metinlerini aktif dile göre güncelle
    # -----------------------------------------------------------------------

    def _retranslate(self):
        self.lbl_mode.setText(t('mode_label'))
        self.btn_mode_new.setText(t('mode_new'))
        self.btn_mode_add.setText(t('mode_add'))
        # Segmented butonların metni kırpılmasın
        for btn in (self.btn_mode_new, self.btn_mode_add):
            fm = btn.fontMetrics()
            btn.setMinimumWidth(fm.horizontalAdvance(btn.text()) + 32)
        self.btn_settings.setText(t('settings_btn'))

        self.lbl_source.setText(t('source_folder'))
        self.edit_source.setPlaceholderText(t('not_selected'))
        self.btn_source.setText(t('select'))

        self.lbl_target.setText(t('target_folder'))
        self.edit_target.setPlaceholderText(t('not_selected'))
        self.btn_target.setText(t('select'))

        self.btn_scan.setText(t('scan'))

        for key, lbl in getattr(self, '_panel_header_labels', {}).items():
            lbl.setText(t(key))

        self.btn_group_event.setText(t('group_event'))
        self.lbl_events.setText(t('events_label'))

        self._lbl_empty.setText(t('empty_state'))

        self.lbl_operation.setText(t('operation'))
        self.btn_op_copy.setText(t('copy'))
        self.btn_op_move.setText(t('move'))
        self.cb_separate.setText(t('separate_types'))
        self.cb_duplicates.setText(t('detect_duplicates'))
        self.lbl_statistics.setText(t('statistics'))

        for key, lbl in getattr(self, '_stat_labels', {}).items():
            lbl.setText(t(key))

        self.lbl_progress.setText(t('ready'))
        self.btn_preview.setText(t('preview_btn'))
        self.btn_start.setText(t('start_btn'))
        self.btn_cancel.setText(t('cancel_btn'))

    # -----------------------------------------------------------------------
    # İkonlar
    # -----------------------------------------------------------------------

    def _apply_icons(self):
        from utils.settings_manager import resolve_theme
        is_dark = resolve_theme() == 'dark'
        fg = '#FFFFFF' if is_dark else '#333333'

        sp = QStyle.StandardPixmap
        s  = self.style()

        # Sol panel
        self.btn_source.setIcon(s.standardIcon(sp.SP_DirOpenIcon))
        self.btn_target.setIcon(s.standardIcon(sp.SP_DirOpenIcon))
        self.btn_scan.setIcon(s.standardIcon(sp.SP_BrowserReload))

        # Mod çubuğu — ayarlar
        self.btn_settings.setIcon(s.standardIcon(sp.SP_FileDialogDetailedView))

        # Alt çubuk — renk duyarlı ikonlar
        self.btn_preview.setIcon(s.standardIcon(sp.SP_FileDialogContentsView))
        self.btn_start.setIcon(self._draw_icon('play', fg))
        self.btn_cancel.setIcon(self._draw_icon('stop', fg))

    @staticmethod
    def _draw_icon(shape: str, color: str, size: int = 14) -> QIcon:
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(color)))
        if shape == 'play':
            pts = [QPointF(2, 1), QPointF(2, size - 1), QPointF(size - 1, size / 2)]
            p.drawPolygon(QPolygonF(pts))
        elif shape == 'stop':
            p.drawRoundedRect(2, 2, size - 4, size - 4, 2, 2)
        p.end()
        return QIcon(px)

    # -----------------------------------------------------------------------
    # Başlangıç durumu
    # -----------------------------------------------------------------------

    def _set_initial_state(self):
        self._update_stats([])
        self.btn_group_event.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(False)

    # -----------------------------------------------------------------------
    # Klasör seçme
    # -----------------------------------------------------------------------

    def _pick_source(self):
        d = QFileDialog.getExistingDirectory(self, t('source_folder'))
        if d:
            self.edit_source.setText(d)

    def _pick_target(self):
        d = QFileDialog.getExistingDirectory(self, t('target_folder'))
        if d:
            self.edit_target.setText(d)

    # -----------------------------------------------------------------------
    # Mod değişikliği
    # -----------------------------------------------------------------------

    def _on_mode_changed(self):
        is_add = self.btn_mode_add.isChecked()
        self.btn_op_move.setEnabled(not is_add)
        if is_add:
            self.btn_op_copy.setChecked(True)

    # -----------------------------------------------------------------------
    # Ayarlar
    # -----------------------------------------------------------------------

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.theme_changed.connect(self._apply_theme)
        dlg.exec()

    def _apply_theme(self, theme_value: str):
        from utils.settings_manager import resolve_theme
        from utils.file_utils import ensure_ui_assets
        resolved = resolve_theme()
        assets = ensure_ui_assets()
        QApplication.instance().setStyleSheet(get_stylesheet(resolved, assets))
        self._apply_icons()

    # -----------------------------------------------------------------------
    # Tarama
    # -----------------------------------------------------------------------

    def _start_scan(self):
        src = self.edit_source.text().strip()
        dst = self.edit_target.text().strip()
        if not src:
            QMessageBox.warning(self, 'PixVault', t('warn_src'))
            return
        if not dst:
            QMessageBox.warning(self, 'PixVault', t('warn_dst'))
            return

        src_path = Path(src)
        dst_path = Path(dst)
        if not src_path.exists():
            QMessageBox.warning(self, 'PixVault', t('warn_src_missing'))
            return
        if src_path.resolve() == dst_path.resolve():
            QMessageBox.warning(self, 'PixVault', t('warn_same_dir'))
            return

        setup_file_logger(Path(dst))

        self._scanned_files = []
        self._event_groups  = []
        self._clear_event_list_ui()
        self.tree.clear()
        self._tree_stack.setCurrentIndex(0)
        self.log_text.clear()

        self._set_buttons_scanning(True)
        self.progress_bar.setValue(0)
        self.lbl_progress.setText(t('scanning'))

        self._scan_worker = ScanWorker(src_path)
        self._scan_worker.progress.connect(self._on_scan_progress)
        self._scan_worker.log_msg.connect(self._append_log)
        self._scan_worker.finished.connect(self._on_scan_finished)
        self._scan_worker.error.connect(self._on_worker_error)
        self._scan_worker.start()

    def _on_scan_progress(self, current: int, total: int):
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.lbl_progress.setText(t('scanning_n', c=current, t=total))

    def _on_scan_finished(self, files: list[FileInfo]):
        self._scanned_files = files
        self._set_buttons_scanning(False)
        self._update_stats(files)
        self._populate_tree(files)
        self._tree_stack.setCurrentIndex(1 if files else 0)

        total = len(files)
        self.lbl_progress.setText(t('scan_done', t=total))
        self.progress_bar.setValue(self.progress_bar.maximum())
        self._append_log('info', t('scan_done_log', t=total))

        self.btn_preview.setEnabled(total > 0)
        self.btn_start.setEnabled(total > 0)

    # -----------------------------------------------------------------------
    # Ağaç görünümü
    # -----------------------------------------------------------------------

    def _populate_tree(self, files: list[FileInfo]):
        self.tree.blockSignals(True)
        self.tree.clear()

        grouped: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        no_date:    list[FileInfo] = []
        duplicates: list[FileInfo] = []

        for fi in files:
            if fi.is_duplicate:
                duplicates.append(fi)
                continue
            if fi.date is None:
                no_date.append(fi)
                continue
            d = fi.date
            grouped[d.year][d.month][d.day].append(fi)

        for year in sorted(grouped.keys(), reverse=True):
            year_item = QTreeWidgetItem([str(year)])
            year_item.setFlags(
                year_item.flags()
                | Qt.ItemFlag.ItemIsAutoTristate
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            year_item.setCheckState(0, Qt.CheckState.Unchecked)
            self.tree.addTopLevelItem(year_item)

            for month in sorted(grouped[year].keys(), reverse=True):
                month_name  = TURKISH_MONTHS[month]
                month_total = sum(len(v) for v in grouped[year][month].values())
                month_item  = QTreeWidgetItem([f'{month_name} ({month_total} dosya)'])
                month_item.setFlags(
                    month_item.flags()
                    | Qt.ItemFlag.ItemIsAutoTristate
                    | Qt.ItemFlag.ItemIsUserCheckable
                )
                month_item.setCheckState(0, Qt.CheckState.Unchecked)
                year_item.addChild(month_item)

                for day in sorted(grouped[year][month].keys()):
                    day_files = grouped[year][month][day]
                    day_label = f'{day:02d} {month_name[:3]}  —  {len(day_files)} dosya'
                    day_item  = QTreeWidgetItem([day_label])
                    day_item.setFlags(day_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    day_item.setCheckState(0, Qt.CheckState.Unchecked)
                    day_item.setData(0, Qt.ItemDataRole.UserRole, date(year, month, day))
                    month_item.addChild(day_item)

            year_item.setExpanded(True)

        if no_date:
            nd = QTreeWidgetItem([f'Tarihsiz ({len(no_date)} dosya)'])
            nd.setForeground(0, QColor('#CCA700'))
            self.tree.addTopLevelItem(nd)

        if duplicates:
            dup = QTreeWidgetItem([f'Tekrarlar ({len(duplicates)} dosya)'])
            dup.setForeground(0, QColor('#F44747'))
            self.tree.addTopLevelItem(dup)

        self.tree.blockSignals(False)

    def _on_tree_item_changed(self, item: QTreeWidgetItem, column: int):
        self.btn_group_event.setEnabled(len(self._get_checked_dates()) > 0)

    def _get_checked_dates(self) -> list[date]:
        dates = []
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            year_item = root.child(i)
            for j in range(year_item.childCount()):
                month_item = year_item.child(j)
                for k in range(month_item.childCount()):
                    day_item = month_item.child(k)
                    if day_item.checkState(0) == Qt.CheckState.Checked:
                        d = day_item.data(0, Qt.ItemDataRole.UserRole)
                        if d:
                            dates.append(d)
        return dates

    def _get_file_count_for_dates(self, dates: list[date]) -> int:
        date_set = set(dates)
        return sum(1 for fi in self._scanned_files if fi.date and fi.date.date() in date_set)

    # -----------------------------------------------------------------------
    # Etkinlik gruplama
    # -----------------------------------------------------------------------

    def _group_as_event(self):
        checked = self._get_checked_dates()
        if not checked:
            return
        dlg = EventDialog(checked, self._get_file_count_for_dates(checked), self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.event_group:
            eg = dlg.event_group
            self._event_groups.append(eg)
            self._add_event_to_ui(eg)
            self._append_log('info', f'Etkinlik: {eg.folder_name}')

    def _add_event_to_ui(self, eg: EventGroup):
        row = QWidget()
        rl  = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(f'• {eg.folder_name}')
        lbl.setWordWrap(True)
        rl.addWidget(lbl, stretch=1)

        btn_edit = QPushButton(t('edit_btn'))
        btn_edit.setObjectName('toolBtn')
        btn_edit.setFixedSize(28, 24)
        btn_edit.setToolTip('Düzenle')

        btn_del = QPushButton(t('delete_btn'))
        btn_del.setObjectName('toolBtn')
        btn_del.setFixedSize(28, 24)
        btn_del.setToolTip('Sil')

        rl.addWidget(btn_edit)
        rl.addWidget(btn_del)

        def edit_event():
            fc  = self._get_file_count_for_dates(eg.dates)
            dlg = EventDialog(eg.dates, fc, self)
            dlg.name_edit.setText(eg.name)
            if dlg.exec() == QDialog.DialogCode.Accepted and dlg.event_group:
                idx = self._event_groups.index(eg)
                self._event_groups[idx] = dlg.event_group
                lbl.setText(f'• {dlg.event_group.folder_name}')
                eg.__dict__.update(dlg.event_group.__dict__)

        def delete_event():
            if eg in self._event_groups:
                self._event_groups.remove(eg)
            self._event_list_layout.removeWidget(row)
            row.deleteLater()

        btn_edit.clicked.connect(edit_event)
        btn_del.clicked.connect(delete_event)
        self._event_list_layout.addWidget(row)

    def _clear_event_list_ui(self):
        while self._event_list_layout.count():
            item = self._event_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # -----------------------------------------------------------------------
    # İstatistik
    # -----------------------------------------------------------------------

    def _update_stats(self, files: list[FileInfo]):
        total   = len(files)
        photos  = sum(1 for f in files if f.file_type == 'photo'   and not f.is_duplicate)
        videos  = sum(1 for f in files if f.file_type == 'video'   and not f.is_duplicate)
        dupes   = sum(1 for f in files if f.is_duplicate)
        no_date = sum(1 for f in files if f.date is None           and not f.is_duplicate)
        unknown = sum(1 for f in files if f.file_type == 'unknown')

        def fmt(n): return str(n) if total else '—'

        self.lbl_total.setText(fmt(total))
        self.lbl_photos.setText(fmt(photos))
        self.lbl_videos.setText(fmt(videos))
        self.lbl_dupes.setText(fmt(dupes))
        self.lbl_no_date.setText(fmt(no_date))
        self.lbl_unknown.setText(fmt(unknown))

    # -----------------------------------------------------------------------
    # Ön izleme / gerçek işlem
    # -----------------------------------------------------------------------

    def _start_preview(self):
        self._run_organize(dry_run=True)

    def _start_organize(self):
        self._run_organize(dry_run=False)

    def _run_organize(self, dry_run: bool):
        dst = self.edit_target.text().strip()
        if not dst:
            QMessageBox.warning(self, 'PixVault', t('warn_dst'))
            return
        if not self._scanned_files:
            QMessageBox.warning(self, 'PixVault', t('warn_scan_first'))
            return

        src = self.edit_source.text().strip()
        if src and Path(src).resolve() == Path(dst).resolve():
            QMessageBox.warning(self, 'PixVault', t('warn_same_dir'))
            return

        if not self.cb_duplicates.isChecked():
            for fi in self._scanned_files:
                fi.is_duplicate = False

        # "Taşı" = önce kopyala, işlem sonrası silme onayı iste
        self._pending_move = (not dry_run) and self.btn_op_move.isChecked()

        self._set_buttons_working(True)
        self.progress_bar.setValue(0)
        self.lbl_progress.setText(t('preview_running') if dry_run else t('working'))

        self._org_worker = OrganizeWorker(
            files          = self._scanned_files,
            target_dir     = Path(dst),
            mode           = 'copy',   # her zaman kopyala; taşıma = kopyala + onaylı sil
            separate_types = self.cb_separate.isChecked(),
            event_groups   = self._event_groups,
            dry_run        = dry_run,
        )
        self._org_worker.progress.connect(self._on_org_progress)
        self._org_worker.log_msg.connect(self._append_log)
        self._org_worker.finished.connect(self._on_org_finished)
        self._org_worker.error.connect(self._on_worker_error)
        self._org_worker.start()

    def _on_org_progress(self, current: int, total: int):
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.lbl_progress.setText(t('n_of_t', c=current, t=total))

    def _on_org_finished(self, result: dict):
        self._set_buttons_working(False)

        if result.get('dry_run'):
            c = len(result.get('plan', []))
            self.lbl_progress.setText(t('preview_done', c=c))
            self._append_log('info', t('preview_done_log', c=c))
            QMessageBox.information(self, t('preview_result_title'), t('preview_result_text', c=c))
        else:
            s  = result.get('success', 0)
            sk = result.get('skipped', 0)
            self.lbl_progress.setText(t('done', s=s, sk=sk))
            self._append_log('info', t('done_log', s=s, sk=sk))
            if self._pending_move:
                self._pending_move = False
                if s > 0:
                    self._show_move_completion(s)
            elif self.btn_mode_add.isChecked():
                self._show_add_mode_completion(s)

    def _show_move_completion(self, count: int):
        src_path = Path(self.edit_source.text().strip())
        src_cnt  = count_files_in_dir(src_path)

        dlg = QMessageBox(self)
        dlg.setWindowTitle(t('transfer_title'))
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setText(
            f'<b>✅ {count} dosya başarıyla arşive kopyalandı.</b><br><br>'
            f'<b>Kaynak klasör:</b> {src_path}<br>'
            f'<b>Kaynak dosya sayısı:</b> {src_cnt}<br><br>'
            f'<span style="color:#D83B01;">⚠ Orijinal dosyalar <b>kalıcı olarak</b> silinecektir.'
            f'<br>Bu işlem <b>geri alınamaz.</b></span>'
        )
        btn_keep   = dlg.addButton(t('keep_originals'),   QMessageBox.ButtonRole.RejectRole)
        btn_delete = dlg.addButton(t('delete_originals'), QMessageBox.ButtonRole.DestructiveRole)
        dlg.setDefaultButton(btn_keep)
        dlg.exec()

        if dlg.clickedButton() == btn_delete:
            paths = [fi.path for fi in self._scanned_files if fi.path.exists()]
            deleted, errors = safe_delete_files(
                paths, log_callback=lambda lvl, msg: self._append_log(lvl, msg)
            )
            self._append_log('info', f'Taşıma tamamlandı. Silindi: {deleted}, hata: {len(errors)}')
            if errors:
                QMessageBox.warning(self, t('delete_errors_title'), t('delete_errors_text', n=len(errors)))

    def _show_add_mode_completion(self, count: int):
        src      = self.edit_target.text().strip()
        src_path = Path(self.edit_source.text().strip())
        src_cnt  = count_files_in_dir(src_path)

        dlg = QMessageBox(self)
        dlg.setWindowTitle(t('transfer_title'))
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.setText(
            f'<b>✅ {t("transfer_title")}</b><br><br>'
            f'{count} dosya başarıyla arşive kopyalandı.<br>'
            f'Orijinal dosyalar hâlâ yerinde duruyor.<br><br>'
            f'<b>Silinecek klasör:</b> {src_path}<br>'
            f'<b>Dosya sayısı:</b> {src_cnt}<br><br>'
            f'<span style="color:#D83B01;">⚠ Bu işlem geri alınamaz.</span>'
        )
        btn_keep   = dlg.addButton(t('keep_originals'),   QMessageBox.ButtonRole.RejectRole)
        btn_delete = dlg.addButton(t('delete_originals'), QMessageBox.ButtonRole.DestructiveRole)
        dlg.setDefaultButton(btn_keep)
        dlg.exec()

        if dlg.clickedButton() == btn_delete:
            paths   = [fi.path for fi in self._scanned_files if not fi.is_duplicate and fi.path.exists()]
            deleted, errors = safe_delete_files(paths, log_callback=lambda lvl, msg: self._append_log(lvl, msg))
            self._append_log('info', f'Silindi: {deleted}, hata: {len(errors)}')
            if errors:
                QMessageBox.warning(self, t('delete_errors_title'), t('delete_errors_text', n=len(errors)))

    # -----------------------------------------------------------------------
    # İptal
    # -----------------------------------------------------------------------

    def _cancel_operation(self):
        if self._scan_worker and self._scan_worker.isRunning():
            self._scan_worker.cancel()
        if self._org_worker and self._org_worker.isRunning():
            self._org_worker.cancel()
        self._set_buttons_working(False)
        self._set_buttons_scanning(False)
        self.lbl_progress.setText(t('cancelled'))

    # -----------------------------------------------------------------------
    # Buton durumları
    # -----------------------------------------------------------------------

    def _set_buttons_scanning(self, on: bool):
        self.btn_scan.setEnabled(not on)
        self.btn_source.setEnabled(not on)
        self.btn_target.setEnabled(not on)
        self.btn_cancel.setEnabled(on)

    def _set_buttons_working(self, on: bool):
        self.btn_start.setEnabled(not on)
        self.btn_preview.setEnabled(not on)
        self.btn_cancel.setEnabled(on)
        self.btn_scan.setEnabled(not on)

    # -----------------------------------------------------------------------
    # Log
    # -----------------------------------------------------------------------

    def _append_log(self, level: str, message: str):
        color = LOG_COLORS.get(level, '#D4D4D4')
        icon  = LOG_ICONS.get(level, ' ')
        self.log_text.append(f'<span style="color:{color};">{icon} {message}</span>')
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
        lvl_map = {'success': 'info', 'warn': 'warning', 'duplicate': 'warning',
                   'error': 'error', 'info': 'info'}
        getattr(get_logger(), lvl_map.get(level, 'info'))(message)

    def _on_worker_error(self, msg: str):
        self._set_buttons_working(False)
        self._set_buttons_scanning(False)
        self._append_log('error', t('unexpected_error', e=msg))
        QMessageBox.critical(self, t('error_title'), msg)

    # -----------------------------------------------------------------------
    # Pencere kapatma
    # -----------------------------------------------------------------------

    def closeEvent(self, event):
        running = (
            (self._scan_worker and self._scan_worker.isRunning()) or
            (self._org_worker  and self._org_worker.isRunning())
        )
        if running:
            reply = QMessageBox.question(
                self, t('exit_title'), t('exit_text'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._cancel_operation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
