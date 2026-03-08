"""
settings_manager.py — Uygulama ayarlarını JSON olarak saklar/yükler.
"""

import json
import sys
from pathlib import Path

_SETTINGS_FILE = Path.home() / '.pixvault' / 'settings.json'

_DEFAULTS = {
    'theme':    'light',   # 'light' | 'dark' | 'auto'
    'language': 'tr',      # 'tr' | 'en'
}

_settings: dict = {}


def _load() -> dict:
    try:
        if _SETTINGS_FILE.exists():
            data = json.loads(_SETTINGS_FILE.read_text(encoding='utf-8'))
            merged = dict(_DEFAULTS)
            merged.update(data)
            return merged
    except Exception:
        pass
    return dict(_DEFAULTS)


def _save() -> None:
    try:
        _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _SETTINGS_FILE.write_text(
            json.dumps(_settings, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
    except Exception:
        pass


def get(key: str):
    if not _settings:
        _settings.update(_load())
    return _settings.get(key, _DEFAULTS.get(key))


def set_value(key: str, value) -> None:
    if not _settings:
        _settings.update(_load())
    _settings[key] = value
    _save()


def load_all() -> dict:
    _settings.update(_load())
    return dict(_settings)


# --- Sistem teması tespiti (Windows) ---

def get_system_theme() -> str:
    """Windows kayıt defterinden sistem temasını okur. 'light' veya 'dark' döndürür."""
    if sys.platform != 'win32':
        return 'light'
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize',
        )
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        return 'light' if value == 1 else 'dark'
    except Exception:
        return 'light'


def resolve_theme() -> str:
    """'auto' ise sistem temasını döndürür, yoksa ayarlı temayı."""
    theme = get('theme')
    if theme == 'auto':
        return get_system_theme()
    return theme or 'light'
