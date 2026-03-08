"""
styles.py — PixVault PyQt6 stylesheet.
Açık ve koyu tema. get_stylesheet(theme, assets) ile çağrılır.
"""

# ---------------------------------------------------------------------------
# Açık tema
# ---------------------------------------------------------------------------

_LIGHT = """
QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
    color: #1A1A1A;
    background-color: #EBEBEB;
}
QMainWindow, QDialog { background-color: #EBEBEB; }

/* === Mod çubuğu === */
#modeBar {
    background-color: #F7F7F7;
    border-bottom: 1px solid #CCCCCC;
    padding: 0 12px;
}

/* === Panel kapsayıcı === */
#leftPanel, #centerPanel, #rightPanel {
    background-color: #F7F7F7;
    border: none;
    border-radius: 0px;
}

/* === Panel başlık çubuğu === */
#panelHeader {
    background-color: #DCDCDC;
    border-bottom: 1px solid #BBBBBB;
    border-left: 3px solid #0078D4;
}
#panelHeaderLabel {
    color: #333333;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.2px;
}

/* === Birincil buton === */
QPushButton {
    background-color: #0078D4;
    color: #FFFFFF;
    border: none;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 10pt;
    font-weight: 500;
    min-height: 26px;
    min-width: 64px;
}
QPushButton:hover    { background-color: #106EBE; }
QPushButton:pressed  { background-color: #005A9E; }
QPushButton:disabled { background-color: #C0C0C0; color: #888888; }

/* === İkincil buton === */
QPushButton#secondaryBtn {
    background-color: #FFFFFF;
    color: #0078D4;
    border: 1.5px solid #0078D4;
    border-radius: 5px;
    min-width: 72px;
}
QPushButton#secondaryBtn:hover    { background-color: #E4EFF9; }
QPushButton#secondaryBtn:pressed  { background-color: #CCE0F5; }
QPushButton#secondaryBtn:disabled { color: #AAAAAA; border-color: #CCCCCC; background-color: #F5F5F5; }

/* === Tehlikeli buton === */
QPushButton#dangerBtn           { background-color: #D83B01; min-width: 120px; border-radius: 5px; }
QPushButton#dangerBtn:hover     { background-color: #B83000; }
QPushButton#dangerBtn:pressed   { background-color: #9A2800; }

/* === Araç butonu === */
QPushButton#toolBtn {
    background-color: #EBEBEB;
    color: #444444;
    border: 1px solid #BBBBBB;
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 9pt;
    min-height: 20px;
    min-width: 24px;
}
QPushButton#toolBtn:hover   { background-color: #D8D8D8; border-color: #999999; }
QPushButton#toolBtn:pressed { background-color: #C8C8C8; }

/* === Segmented buton === */
QPushButton#segBtnLeft {
    background: transparent;
    color: #0078D4;
    border: 1.5px solid #0078D4;
    border-right: none;
    border-radius: 5px 0 0 5px;
    padding: 4px 16px;
    min-width: 0;
    font-weight: 500;
}
QPushButton#segBtnRight {
    background: transparent;
    color: #0078D4;
    border: 1.5px solid #0078D4;
    border-radius: 0 5px 5px 0;
    padding: 4px 16px;
    min-width: 0;
    font-weight: 500;
}
QPushButton#segBtnLeft:hover:!checked, QPushButton#segBtnRight:hover:!checked { background-color: #EAF2FC; }
QPushButton#segBtnLeft:checked, QPushButton#segBtnRight:checked { background-color: #0078D4; color: #FFFFFF; }
QPushButton#segBtnLeft:checked:hover, QPushButton#segBtnRight:checked:hover { background-color: #106EBE; }
QPushButton#segBtnLeft:disabled, QPushButton#segBtnRight:disabled { color: #AAAAAA; border-color: #CCCCCC; background: transparent; }

/* === Boş durum === */
#emptyStateLabel { color: #999999; font-size: 11pt; }

/* === Metin girişi === */
QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #BBBBBB;
    border-radius: 4px;
    padding: 3px 7px;
    min-height: 24px;
}
QLineEdit:focus     { border-color: #0078D4; }
QLineEdit:read-only { background-color: #F0F0F0; color: #666666; }

/* === Radio buton === */
QRadioButton { spacing: 7px; color: #1A1A1A; }
QRadioButton::indicator {
    width: 16px; height: 16px;
    border-radius: 8px;
    border: 1.5px solid #AAAAAA;
    background: #FFFFFF;
}
QRadioButton::indicator:hover   { border-color: #0078D4; background: #EEF5FC; border-radius: 8px; }
QRadioButton::indicator:checked { border: 2px solid #0078D4; background-color: #0078D4; border-radius: 8px; }
QRadioButton::indicator:checked:hover { border-color: #106EBE; background-color: #106EBE; border-radius: 8px; }

/* === Checkbox === */
QCheckBox { spacing: 8px; color: #1A1A1A; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    border: 1.5px solid #888888;
    border-radius: 2px;
    background: #FFFFFF;
}
QCheckBox::indicator:hover   { border-color: #0078D4; }
QCheckBox::indicator:checked {
    border: 1.5px solid #0078D4;
    background-color: #0078D4;
    image: url(CHECK_WHITE_URL);
}
QCheckBox::indicator:checked:hover { background-color: #106EBE; }

/* === Ağaç görünümü === */
QTreeWidget {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 0px;
    outline: none;
    alternate-background-color: #F5F5F5;
}
QTreeWidget::item          { padding: 3px 5px; }
QTreeWidget::item:hover    { background-color: #DDE8F5; }
QTreeWidget::item:selected { background-color: #B8D4EE; color: #1A1A1A; }
QTreeWidget::branch        { background-color: transparent; }

/* === İlerleme çubuğu === */
QProgressBar {
    background-color: #DDDDDD;
    border: none;
    border-radius: 3px;
    height: 8px;
}
QProgressBar::chunk { background-color: #0078D4; border-radius: 3px; }

/* === Log alanı === */
#logArea {
    background-color: #1A1A1A;
    color: #CCCCCC;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 8.5pt;
    border: none;
    border-top: 1px solid #BBBBBB;
    padding: 5px 8px;
}

/* === Etiketler === */
QLabel#fieldLabel {
    font-size: 8.5pt;
    color: #555555;
    font-weight: 600;
}
QLabel#statsValue {
    font-size: 10pt;
    font-weight: 700;
    color: #0078D4;
}

/* === Alt çubuk === */
#bottomBar {
    background-color: #E0E0E0;
    border-top: 1px solid #BBBBBB;
}

/* === GroupBox === */
QGroupBox {
    border: none;
    margin-top: 0;
    padding: 4px;
}

/* === Scrollbar === */
QScrollBar:vertical   { background: #E8E8E8; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #BBBBBB; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #0078D4; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #E8E8E8; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #BBBBBB; border-radius: 4px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #0078D4; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""

# ---------------------------------------------------------------------------
# Koyu tema — Nikon Transfer 2 benzeri profesyonel koyu görünüm
# ---------------------------------------------------------------------------

_DARK = """
QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
    color: #D4D4D4;
    background-color: #1E1E1E;
}
QMainWindow, QDialog { background-color: #1E1E1E; }

/* === Mod çubuğu === */
#modeBar {
    background-color: #2A2A2A;
    border-bottom: 1px solid #3C3C3C;
    padding: 0 12px;
}

/* === Panel kapsayıcı === */
#leftPanel, #centerPanel, #rightPanel {
    background-color: #252525;
    border: none;
    border-radius: 0px;
}

/* === Panel başlık çubuğu === */
#panelHeader {
    background-color: #1A1A1A;
    border-bottom: 1px solid #383838;
    border-left: 3px solid #0078D4;
}
#panelHeaderLabel {
    color: #AAAAAA;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.2px;
}

/* === Birincil buton === */
QPushButton {
    background-color: #0078D4;
    color: #FFFFFF;
    border: none;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 10pt;
    font-weight: 500;
    min-height: 26px;
    min-width: 64px;
}
QPushButton:hover    { background-color: #1A8AE0; }
QPushButton:pressed  { background-color: #0063B1; }
QPushButton:disabled { background-color: #383838; color: #666666; }

/* === İkincil buton === */
QPushButton#secondaryBtn {
    background-color: #2E2E2E;
    color: #4DB8FF;
    border: 1.5px solid #4DB8FF;
    border-radius: 5px;
    min-width: 72px;
}
QPushButton#secondaryBtn:hover    { background-color: #3A4A5C; }
QPushButton#secondaryBtn:pressed  { background-color: #2C3C4E; }
QPushButton#secondaryBtn:disabled { color: #555555; border-color: #444444; background-color: #262626; }

/* === Tehlikeli buton === */
QPushButton#dangerBtn           { background-color: #C0392B; min-width: 120px; border-radius: 5px; }
QPushButton#dangerBtn:hover     { background-color: #A93226; }
QPushButton#dangerBtn:pressed   { background-color: #922B21; }

/* === Araç butonu === */
QPushButton#toolBtn {
    background-color: #333333;
    color: #CCCCCC;
    border: 1px solid #4A4A4A;
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 9pt;
    min-height: 20px;
    min-width: 24px;
}
QPushButton#toolBtn:hover   { background-color: #404040; border-color: #666666; }
QPushButton#toolBtn:pressed { background-color: #2A2A2A; }

/* === Segmented buton === */
QPushButton#segBtnLeft {
    background: transparent;
    color: #4DB8FF;
    border: 1.5px solid #4DB8FF;
    border-right: none;
    border-radius: 5px 0 0 5px;
    padding: 4px 16px;
    min-width: 0;
    font-weight: 500;
}
QPushButton#segBtnRight {
    background: transparent;
    color: #4DB8FF;
    border: 1.5px solid #4DB8FF;
    border-radius: 0 5px 5px 0;
    padding: 4px 16px;
    min-width: 0;
    font-weight: 500;
}
QPushButton#segBtnLeft:hover:!checked, QPushButton#segBtnRight:hover:!checked { background-color: #1A3A5C; }
QPushButton#segBtnLeft:checked, QPushButton#segBtnRight:checked { background-color: #0078D4; color: #FFFFFF; border-color: #0078D4; }
QPushButton#segBtnLeft:checked:hover, QPushButton#segBtnRight:checked:hover { background-color: #1A8AE0; }
QPushButton#segBtnLeft:disabled, QPushButton#segBtnRight:disabled { color: #555555; border-color: #444444; background: transparent; }

/* === Boş durum === */
#emptyStateLabel { color: #555555; font-size: 11pt; }

/* === Metin girişi === */
QLineEdit {
    background-color: #2E2E2E;
    border: 1px solid #4A4A4A;
    border-radius: 4px;
    padding: 3px 7px;
    color: #D4D4D4;
    min-height: 24px;
}
QLineEdit:focus     { border-color: #4DB8FF; }
QLineEdit:read-only { background-color: #242424; color: #777777; }

/* === Radio buton === */
QRadioButton { color: #D4D4D4; spacing: 7px; }
QRadioButton::indicator {
    width: 16px; height: 16px;
    border-radius: 8px;
    border: 1.5px solid #666666;
    background: #2E2E2E;
}
QRadioButton::indicator:hover   { border-color: #4DB8FF; border-radius: 8px; }
QRadioButton::indicator:checked { border: 2px solid #4DB8FF; background-color: #0078D4; border-radius: 8px; }
QRadioButton::indicator:checked:hover { background-color: #1A8AE0; border-color: #80CFFF; border-radius: 8px; }

/* === Checkbox === */
QCheckBox { color: #D4D4D4; spacing: 8px; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    border: 1.5px solid #5A5A5A;
    border-radius: 2px;
    background: #2E2E2E;
}
QCheckBox::indicator:hover   { border-color: #4DB8FF; }
QCheckBox::indicator:checked {
    border: 1.5px solid #4DB8FF;
    background-color: #0078D4;
    image: url(CHECK_WHITE_URL);
}
QCheckBox::indicator:checked:hover { background-color: #1A8AE0; border-color: #80CFFF; }

/* === Ağaç görünümü === */
QTreeWidget {
    background-color: #2A2A2A;
    border: 1px solid #383838;
    border-radius: 0px;
    outline: none;
    color: #D4D4D4;
    alternate-background-color: #2E2E2E;
}
QTreeWidget::item          { padding: 3px 5px; }
QTreeWidget::item:hover    { background-color: #344A5E; }
QTreeWidget::item:selected { background-color: #1A4A6E; color: #E8E8E8; }
QTreeWidget::branch        { background-color: transparent; }

/* === İlerleme çubuğu === */
QProgressBar {
    background-color: #383838;
    border: none;
    border-radius: 3px;
    height: 8px;
}
QProgressBar::chunk { background-color: #0078D4; border-radius: 3px; }

/* === Log alanı === */
#logArea {
    background-color: #111111;
    color: #CCCCCC;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 8.5pt;
    border: none;
    border-top: 1px solid #383838;
    padding: 5px 8px;
}

/* === Etiketler === */
QLabel#fieldLabel { font-size: 8.5pt; color: #888888; font-weight: 600; }
QLabel#statsValue { font-size: 10pt; font-weight: 700; color: #4DB8FF; }

/* === Alt çubuk === */
#bottomBar {
    background-color: #1A1A1A;
    border-top: 1px solid #383838;
}

/* === GroupBox === */
QGroupBox {
    border: none;
    margin-top: 0;
    padding: 4px;
    color: #D4D4D4;
}

/* === Scrollbar === */
QScrollBar:vertical   { background: #1E1E1E; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #4A4A4A; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #0078D4; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1E1E1E; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #4A4A4A; border-radius: 4px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #0078D4; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""

# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

LOG_COLORS = {
    'success':   '#4EC9B0',
    'warn':      '#CCA700',
    'duplicate': '#F44747',
    'error':     '#F44747',
    'info':      '#569CD6',
}

LOG_ICONS = {
    'success':   '✅',
    'warn':      '⚠',
    'duplicate': '🔴',
    'error':     '🔴',
    'info':      'ℹ',
}

MAIN_STYLE = _LIGHT


def get_stylesheet(theme: str, assets: dict = None) -> str:
    sheet = _DARK if theme == 'dark' else _LIGHT
    check_url = (assets or {}).get('check_white', '')
    return sheet.replace('CHECK_WHITE_URL', check_url)
