"""
organizer.py — Klasörleme ve kopyalama/taşıma mantığı.
"""

import shutil
from pathlib import Path
from datetime import date
from typing import Optional

from core.scanner import FileInfo, PHOTO_EXTENSIONS, VIDEO_EXTENSIONS
from core.event_group import EventGroup, TURKISH_MONTHS


class Organizer:
    """
    Tarama sonucunu alır, hedef klasörde arşiv yapısını oluşturur.

    Mod A: sıfırdan yeni arşiv
    Mod B: mevcut arşive ekle (sadece kopyala)
    """

    def __init__(
        self,
        target_dir: Path,
        mode: str = 'copy',          # 'copy' | 'move'
        separate_types: bool = True,  # Fotoğraf/Video ayrı klasör
        event_groups: Optional[list[EventGroup]] = None,
        progress_callback=None,
        log_callback=None,
    ):
        self.target_dir = target_dir
        self.mode = mode
        self.separate_types = separate_types
        self.event_groups = event_groups or []
        self._progress_cb = progress_callback
        self._log_cb = log_callback
        self._cancelled = False

        self._duplicates_dir = target_dir / 'Tekrarlar'
        self._no_date_dir = target_dir / 'Tarihsiz'

    def cancel(self):
        self._cancelled = True

    # ------------------------------------------------------------------
    # Dry-run (ön izleme) — dosyaya dokunmaz
    # ------------------------------------------------------------------

    def dry_run(self, files: list[FileInfo]) -> list[dict]:
        """Her dosya için {'src', 'dst', 'action'} sözlüğü döndürür."""
        plan = []
        for fi in files:
            if self._cancelled:
                break
            dst = self._resolve_destination(fi)
            action = 'duplicate' if fi.is_duplicate else self.mode
            plan.append({'src': fi.path, 'dst': dst, 'action': action, 'info': fi})
        return plan

    # ------------------------------------------------------------------
    # Gerçek işlem
    # ------------------------------------------------------------------

    def run(self, files: list[FileInfo]) -> dict:
        """
        Dosyaları taşır/kopyalar.
        Döndürür: {'success': int, 'skipped': int, 'errors': list[str]}
        """
        total = len(files)
        success = 0
        skipped = 0
        errors = []

        for i, fi in enumerate(files):
            if self._cancelled:
                break

            dst = self._resolve_destination(fi)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst = self._unique_path(dst)

            try:
                if self.mode == 'copy':
                    shutil.copy2(str(fi.path), str(dst))
                else:
                    shutil.move(str(fi.path), str(dst))
                success += 1
                self._log('success', f'{fi.path.name} → {dst.relative_to(self.target_dir)}')
            except Exception as e:
                skipped += 1
                msg = f'HATA {fi.path.name}: {e}'
                errors.append(msg)
                self._log('error', msg)

            if self._progress_cb:
                self._progress_cb(i + 1, total)

        return {'success': success, 'skipped': skipped, 'errors': errors}

    # ------------------------------------------------------------------
    # Hedef yolu belirleme
    # ------------------------------------------------------------------

    def _resolve_destination(self, fi: FileInfo) -> Path:
        if fi.is_duplicate:
            return self._duplicates_dir / fi.path.name

        # Mesajlaşma/sosyal medya kaynaklı dosyalar — ayrı klasör
        if fi.source_app in ('whatsapp', 'telegram', 'social_media'):
            return self._resolve_messenger_destination(fi)

        if fi.date is None:
            if self.separate_types:
                sub = self._type_folder(fi)
                return self._no_date_dir / sub / fi.path.name
            return self._no_date_dir / fi.path.name

        d = fi.date.date()

        # Etkinlik grubu kontrolü
        for event in self.event_groups:
            if event.contains_date(d):
                event_dir = self._month_dir(d) / event.folder_name
                if fi.file_type == 'video':
                    return event_dir / 'Video' / fi.path.name
                return event_dir / fi.path.name

        # Normal ay/tür klasörü
        month_dir = self._month_dir(d)
        if self.separate_types:
            return month_dir / self._type_folder(fi) / fi.path.name
        return month_dir / fi.path.name

    def _type_folder(self, fi: FileInfo) -> str:
        """'Fotoğraflar (iPhone)' veya 'Videolar (Samsung)' gibi tür/marka klasör adı."""
        base = 'Fotoğraflar' if fi.file_type == 'photo' else 'Videolar'
        if fi.camera_label:
            return f'{base} ({fi.camera_label})'
        return base

    def _resolve_messenger_destination(self, fi: FileInfo) -> Path:
        app_name = {
            'whatsapp':     'WhatsApp',
            'telegram':     'Telegram',
            'social_media': 'Sosyal Medya',
        }.get(fi.source_app, 'Sosyal Medya')

        if fi.date is None:
            return self._no_date_dir / app_name / fi.path.name

        return self._month_dir(fi.date.date()) / app_name / fi.path.name

    def _month_dir(self, d: date) -> Path:
        year_str = str(d.year)
        month_str = f'{d.year}-{d.month:02d} {TURKISH_MONTHS[d.month]}'
        return self.target_dir / year_str / month_str

    @staticmethod
    def _unique_path(dst: Path) -> Path:
        if not dst.exists():
            return dst
        stem = dst.stem
        suffix = dst.suffix
        parent = dst.parent
        counter = 1
        while True:
            candidate = parent / f'{stem}_{counter:02d}{suffix}'
            if not candidate.exists():
                return candidate
            counter += 1

    def _log(self, level: str, message: str):
        if self._log_cb:
            self._log_cb(level, message)
