"""
scanner.py — Dosya tarama ve metadata okuma modülü.
Fotoğraf EXIF ve video metadata'sından tarih bilgisi çıkarır.
"""

import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from PIL import Image
import piexif

try:
    from pymediainfo import MediaInfo
    MEDIAINFO_AVAILABLE = True
except Exception:
    MEDIAINFO_AVAILABLE = False


PHOTO_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.heic', '.heif',
    '.raw', '.cr2', '.cr3', '.nef', '.arw', '.dng', '.tiff', '.bmp'
}

VIDEO_EXTENSIONS = {
    '.mp4', '.mov', '.avi', '.mkv', '.m4v', '.3gp', '.wmv'
}

# Dosya adındaki tarih desenleri
FILENAME_DATE_PATTERNS = [
    re.compile(r'(\d{4})(\d{2})(\d{2})[_\-]'),   # 20240815_  veya 20240815-
    re.compile(r'[_\-](\d{4})(\d{2})(\d{2})[_\-]'),  # IMG-20240815-
    re.compile(r'[_\-](\d{4})(\d{2})(\d{2})$'),   # sonda YYYYMMDD
]

# piexif yalnızca JPEG ve TIFF okuyabilir
_PIEXIF_EXTENSIONS = {'.jpg', '.jpeg', '.tiff', '.tif'}

# WhatsApp: IMG-20240815-WA0001.jpg  /  WhatsApp Image 2024-08-15 at ...jpeg
_WA_FILENAME_RE = re.compile(r'-WA\d{4}\.', re.IGNORECASE)
_WA_PREFIX_RE   = re.compile(r'^WhatsApp\s', re.IGNORECASE)

# EXIF Make alanı → kısa marka adı eşleştirmesi
_MAKE_MAP: dict[str, str] = {
    'apple':             'iPhone',
    'samsung':           'Samsung',
    'huawei':            'Huawei',
    'honor':             'Honor',
    'google':            'Google',
    'oneplus':           'OnePlus',
    'xiaomi':            'Xiaomi',
    'oppo':              'OPPO',
    'vivo':              'Vivo',
    'realme':            'Realme',
    'motorola':          'Motorola',
    'lg electronics':    'LG',
    'lg':                'LG',
    'sony':              'Sony',
    'canon':             'Canon',
    'nikon corporation': 'Nikon',
    'nikon':             'Nikon',
    'panasonic':         'Panasonic',
    'fujifilm':          'Fujifilm',
    'olympus':           'Olympus',
    'gopro':             'GoPro',
    'dji':               'DJI',
}


def _normalize_make(make: str) -> str:
    """EXIF Make → kısa, okunabilir marka adı."""
    raw = make.strip()
    return _MAKE_MAP.get(raw.lower(), raw.title() if raw else '')


def _detect_source_app(path: Path) -> str:
    """Dosyanın WhatsApp/Telegram'dan gelip gelmediğini saptar."""
    for parent in path.parents:
        pname = parent.name.lower()
        if 'whatsapp' in pname:
            return 'whatsapp'
        if 'telegram' in pname:
            return 'telegram'
    name = path.name
    if _WA_FILENAME_RE.search(name):
        return 'whatsapp'
    if _WA_PREFIX_RE.match(name):
        return 'whatsapp'
    return ''


@dataclass
class FileInfo:
    path: Path
    file_type: str          # 'photo' | 'video' | 'unknown'
    date: Optional[datetime] = None
    date_source: str = ''   # 'exif' | 'metadata' | 'filename' | 'filesystem' | 'none'
    size: int = 0
    md5: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of: Optional[Path] = None
    error: Optional[str] = None
    source_app: str = ''    # 'whatsapp' | 'telegram' | 'social_media' | ''
    camera_label: str = ''  # 'iPhone' | 'Samsung' | 'Nikon' | ... | ''

    def __post_init__(self):
        self.size = self.path.stat().st_size if self.path.exists() else 0


class Scanner:
    """Kaynak klasörü tarayarak FileInfo listesi döndürür."""

    def __init__(self, progress_callback=None, log_callback=None):
        """
        progress_callback(current: int, total: int)
        log_callback(level: str, message: str)
        """
        self._progress_cb = progress_callback
        self._log_cb = log_callback
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def scan(self, source_dir: Path) -> list[FileInfo]:
        self._cancelled = False
        all_files = [
            p for p in source_dir.rglob('*')
            if p.is_file()
        ]
        total = len(all_files)
        results: list[FileInfo] = []

        for i, path in enumerate(all_files):
            if self._cancelled:
                break
            info = self._process_file(path)
            results.append(info)
            if self._progress_cb:
                self._progress_cb(i + 1, total)

        return results

    # ------------------------------------------------------------------
    # Dahili yardımcılar
    # ------------------------------------------------------------------

    def _process_file(self, path: Path) -> FileInfo:
        ext = path.suffix.lower()
        source_app   = _detect_source_app(path)  # 1. adım: ad/klasör kontrolü
        camera_label = ''

        if ext in PHOTO_EXTENSIONS:
            file_type = 'photo'
            date, date_src = self._get_photo_date(path)
            # 2. adım: ad/klasörden kaynak tespit edilemezse EXIF'e bak
            if not source_app:
                source_app = self._check_exif_source(path)
            # Gerçek kamera çekimi ise marka etiketini al
            if not source_app:
                camera_label = self._get_camera_label_photo(path)
        elif ext in VIDEO_EXTENSIONS:
            file_type = 'video'
            date, date_src = self._get_video_date(path)
            if not source_app:
                camera_label = self._get_camera_label_video(path)
        else:
            file_type = 'unknown'
            date, date_src = None, 'none'
            self._log('info', f'Desteklenmeyen uzantı atlandı: {path.name}')
            return FileInfo(path=path, file_type=file_type, date=date,
                            date_source=date_src, source_app=source_app)

        if date is None:
            date, date_src = self._get_filename_date(path)

        if date is None:
            date, date_src = self._get_filesystem_date(path)
            if date:
                date_src = 'filesystem'

        return FileInfo(path=path, file_type=file_type, date=date,
                        date_source=date_src, source_app=source_app,
                        camera_label=camera_label)

    # --- Fotoğraf EXIF ---

    def _get_photo_date(self, path: Path) -> tuple[Optional[datetime], str]:
        ext = path.suffix.lower()

        # piexif yalnızca JPEG/TIFF destekler; diğer formatlarda bu adımı atla
        if ext in _PIEXIF_EXTENSIONS:
            try:
                exif_data = piexif.load(str(path))
                for ifd in ('Exif', '0th', '1st'):
                    if ifd not in exif_data:
                        continue
                    for tag_id in (piexif.ExifIFD.DateTimeOriginal, piexif.ExifIFD.DateTimeDigitized):
                        val = exif_data[ifd].get(tag_id)
                        if val:
                            dt = self._parse_exif_date(val.decode('ascii', errors='ignore'))
                            if dt:
                                return dt, 'exif'
            except Exception as e:
                self._log('warn', f'EXIF okunamadı {path.name}: {e}')

        # Pillow ile genel EXIF okuma (HEIC, PNG, RAW vs.)
        try:
            with Image.open(path) as img:
                exif_info = img.getexif()
                if exif_info:
                    for tag_id in (36867, 36868, 306):  # DateTimeOriginal, DateTimeDigitized, DateTime
                        val = exif_info.get(tag_id)
                        if val:
                            dt = self._parse_exif_date(str(val))
                            if dt:
                                return dt, 'exif'
        except Exception:
            pass  # Pillow bu formatı açamıyorsa sessizce geç

        return None, ''

    def _get_camera_label_photo(self, path: Path) -> str:
        """EXIF Make alanından normalize edilmiş marka etiketini döndürür."""
        try:
            with Image.open(path) as img:
                exif = img.getexif()
                if exif:
                    make = str(exif.get(271, '')).strip()  # tag 271 = Make
                    if make:
                        return _normalize_make(make)
        except Exception:
            pass
        return ''

    def _get_camera_label_video(self, path: Path) -> str:
        """pymediainfo üzerinden video dosyasının kamera markasını okur."""
        if not MEDIAINFO_AVAILABLE:
            return ''
        try:
            media = MediaInfo.parse(str(path))
            for track in media.tracks:
                # QuickTime/MP4 genel track'te bazen 'make' veya 'com_apple_quicktime_make' gelir
                for attr in ('make', 'com_apple_quicktime_make', 'performer'):
                    val = getattr(track, attr, None)
                    if val:
                        label = _normalize_make(str(val))
                        if label:
                            return label
        except Exception:
            pass
        return ''

    def _check_exif_source(self, path: Path) -> str:
        """
        EXIF Make/Model/Software etiketlerinden kaynağı tahmin eder.
        - Software == 'WhatsApp'  → 'whatsapp'
        - Make ve Model tamamen boş → 'social_media'  (WhatsApp/sosyal medya EXIF kamera bilgisini siler)
        - Kamera bilgisi var        → '' (gerçek çekim)
        """
        try:
            with Image.open(path) as img:
                exif = img.getexif()
                if not exif:
                    return 'social_media'
                # tag 305 = Software
                software = str(exif.get(305, '')).lower()
                if 'whatsapp' in software:
                    return 'whatsapp'
                # tag 271 = Make, 272 = Model
                make  = exif.get(271, '')
                model = exif.get(272, '')
                if not make and not model:
                    return 'social_media'
        except Exception:
            pass
        return ''

    @staticmethod
    def _parse_exif_date(value: str) -> Optional[datetime]:
        value = value.strip().replace('\x00', '')
        for fmt in ('%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S'):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
        return None

    # --- Video metadata ---

    def _get_video_date(self, path: Path) -> tuple[Optional[datetime], str]:
        if not MEDIAINFO_AVAILABLE:
            return None, ''
        try:
            media = MediaInfo.parse(str(path))
            for track in media.tracks:
                for attr in ('encoded_date', 'tagged_date', 'recorded_date'):
                    val = getattr(track, attr, None)
                    if val:
                        dt = self._parse_media_date(str(val))
                        if dt:
                            return dt, 'metadata'
        except Exception as e:
            self._log('warn', f'Video metadata okunamadı {path.name}: {e}')
        return None, ''

    @staticmethod
    def _parse_media_date(value: str) -> Optional[datetime]:
        # "UTC 2024-08-15 10:30:00" veya "2024-08-15T10:30:00+00:00"
        value = value.replace('UTC ', '').strip()
        for fmt in (
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d',
        ):
            try:
                dt = datetime.strptime(value[:19], fmt[:len(fmt)])
                return dt.replace(tzinfo=None)
            except ValueError:
                pass
        return None

    # --- Dosya adından tarih ---

    def _get_filename_date(self, path: Path) -> tuple[Optional[datetime], str]:
        stem = path.stem
        for pattern in FILENAME_DATE_PATTERNS:
            m = pattern.search(stem)
            if m:
                try:
                    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    if 1990 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                        return datetime(year, month, day), 'filename'
                except (ValueError, IndexError):
                    pass
        return None, ''

    # --- Dosya sistemi tarihi ---

    @staticmethod
    def _get_filesystem_date(path: Path) -> tuple[Optional[datetime], str]:
        try:
            stat = path.stat()
            ts = min(stat.st_mtime, stat.st_ctime)
            return datetime.fromtimestamp(ts), 'filesystem'
        except Exception:
            return None, 'none'

    def _log(self, level: str, message: str):
        if self._log_cb:
            self._log_cb(level, message)
