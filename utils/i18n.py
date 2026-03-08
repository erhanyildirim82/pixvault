"""
i18n.py — Çoklu dil desteği (Türkçe / İngilizce).
"""

_lang: str = 'tr'

STRINGS: dict[str, dict[str, str]] = {
    'tr': {
        # Mod çubuğu
        'mode_label':           'Mod:',
        'mode_new':             'Yeni Arşiv Oluştur',
        'mode_add':             'Mevcut Arşive Ekle',
        'settings_btn':         'Ayarlar',

        # Panel başlıkları
        'panel_folders':        'KLASÖRLER',
        'panel_scan':           'TARAMA SONUÇLARI',
        'panel_options':        'SEÇENEKLER',

        # Sol panel
        'source_folder':        'Kaynak Klasör',
        'target_folder':        'Hedef / Arşiv Klasörü',
        'not_selected':         'Seçilmedi...',
        'select':               'Seç',
        'scan':                 'Tara',

        # Orta panel
        'scan_results':         'Tarama Sonuçları',
        'empty_state':          'Kaynak klasörü seçin ve\n"Tara" butonuna basın',
        'group_event':          '✦  Etkinlik Olarak Grupla',
        'events_label':         'Etkinlikler:',
        'edit_btn':             '✎',
        'delete_btn':           '✕',

        # Sağ panel
        'operation':            'İşlem',
        'copy':                 'Kopyala',
        'move':                 'Taşı',
        'separate_types':       'Foto/Video ayrı klasör',
        'detect_duplicates':    'Duplikat tespiti',
        'statistics':           'İstatistik',
        'total':                'Toplam:',
        'photos':               'Fotoğraf:',
        'videos':               'Video:',
        'dupes':                'Duplikat:',
        'no_date':              'Tarihsiz:',
        'other':                'Diğer:',

        # Alt çubuk
        'ready':                'Hazır',
        'preview_btn':          'Ön İzle',
        'start_btn':            'Başlat',
        'cancel_btn':           'İptal',

        # Durum mesajları
        'scanning':             'Taranıyor...',
        'scanning_n':           'Taranıyor... {c}/{t}',
        'scan_done':            'Tamamlandı — {t} dosya',
        'scan_done_log':        'Tarama tamamlandı. {t} dosya bulundu.',
        'preview_running':      'Ön izleme çalışıyor...',
        'working':              'İşlem devam ediyor...',
        'n_of_t':               '{c}/{t} dosya',
        'preview_done':         'Ön izleme — {c} dosya',
        'preview_done_log':     'Ön izleme: {c} dosya planlandı.',
        'done':                 'Tamamlandı — {s} başarılı, {sk} atlanan',
        'done_log':             'İşlem tamamlandı. Başarılı: {s}, Atlanan: {sk}',
        'cancelled':            'İptal edildi',

        # Uyarı / dialog
        'warn_src':             'Kaynak klasörü seçin.',
        'warn_dst':             'Hedef klasörü seçin.',
        'warn_src_missing':     'Kaynak klasör bulunamadı.',
        'warn_same_dir':        'Kaynak ve hedef klasör aynı olamaz.',
        'warn_scan_first':      'Önce tarama yapın.',
        'error_title':          'Hata',
        'unexpected_error':     'Beklenmeyen hata: {e}',
        'exit_title':           'Çıkış',
        'exit_text':            'Bir işlem devam ediyor. Çıkmak istiyor musunuz?',
        'delete_errors_title':  'Silme Hataları',
        'delete_errors_text':   '{n} dosya silinemedi. Log dosyasını kontrol edin.',

        # Özet dialog
        'preview_result_title': 'Ön İzleme Sonucu',
        'preview_result_text':  '{c} dosya düzenlenecek.\n\nİşlemi başlatmak için "Başlat" butonuna tıklayın.',
        'transfer_title':       'Aktarım Tamamlandı',
        'keep_originals':       'Şimdi Silme',
        'delete_originals':     'Orijinalleri Sil',

        # Etkinlik dialog
        'event_dlg_title':      'Etkinlik Adı Ver',
        'event_days':           'Seçili günler:',
        'event_file_count':     'Toplam dosya:',
        'event_name_lbl':       'Etkinlik adı:',
        'event_placeholder':    'Örn. Kayak Tatili',
        'event_folder_lbl':     'Oluşacak klasör:',
        'ok':                   'Tamam',
        'cancel':               'İptal',

        # Ayarlar dialog
        'settings_title':       'Ayarlar',
        'theme_section':        'Tema',
        'theme_light':          'Açık',
        'theme_dark':           'Koyu',
        'theme_auto':           'Otomatik (Sistem)',
        'lang_section':         'Dil / Language',
        'about_section':        'Hakkında',
        'about_desc':           'Fotoğraf ve video dosyalarını otomatik olarak\ntarih ve türe göre arşivleyen masaüstü uygulaması.',
        'close':                'Kapat',
        'restart_note':         'Dil değişikliği için uygulamayı yeniden başlatın.',
    },
    'en': {
        # Mode bar
        'mode_label':           'Mode:',
        'mode_new':             'Create New Archive',
        'mode_add':             'Add to Existing Archive',
        'settings_btn':         'Settings',

        # Left panel
        'source_folder':        'Source Folder',
        'target_folder':        'Target / Archive Folder',
        'not_selected':         'Not selected...',
        'select':               'Select',
        'scan':                 'Scan',

        # Panel headers
        'panel_folders':        'FOLDERS',
        'panel_scan':           'SCAN RESULTS',
        'panel_options':        'OPTIONS',

        # Center panel
        'scan_results':         'Scan Results',
        'empty_state':          'Select a source folder and\nclick "Scan" to begin',
        'group_event':          '✦  Group as Event',
        'events_label':         'Events:',
        'edit_btn':             '✎',
        'delete_btn':           '✕',

        # Right panel
        'operation':            'Operation',
        'copy':                 'Copy',
        'move':                 'Move',
        'separate_types':       'Separate Photo/Video folders',
        'detect_duplicates':    'Detect duplicates',
        'statistics':           'Statistics',
        'total':                'Total:',
        'photos':               'Photos:',
        'videos':               'Videos:',
        'dupes':                'Duplicates:',
        'no_date':              'No date:',
        'other':                'Other:',

        # Bottom bar
        'ready':                'Ready',
        'preview_btn':          'Preview',
        'start_btn':            'Start',
        'cancel_btn':           'Cancel',

        # Status messages
        'scanning':             'Scanning...',
        'scanning_n':           'Scanning... {c}/{t}',
        'scan_done':            'Complete — {t} files',
        'scan_done_log':        'Scan complete. {t} files found.',
        'preview_running':      'Preview running...',
        'working':              'Processing...',
        'n_of_t':               '{c}/{t} files',
        'preview_done':         'Preview — {c} files',
        'preview_done_log':     'Preview: {c} files planned.',
        'done':                 'Complete — {s} success, {sk} skipped',
        'done_log':             'Complete. Success: {s}, Skipped: {sk}',
        'cancelled':            'Cancelled',

        # Warnings / dialogs
        'warn_src':             'Please select a source folder.',
        'warn_dst':             'Please select a target folder.',
        'warn_src_missing':     'Source folder not found.',
        'warn_same_dir':        'Source and target folders cannot be the same.',
        'warn_scan_first':      'Please scan first.',
        'error_title':          'Error',
        'unexpected_error':     'Unexpected error: {e}',
        'exit_title':           'Exit',
        'exit_text':            'An operation is in progress. Do you want to exit?',
        'delete_errors_title':  'Delete Errors',
        'delete_errors_text':   '{n} file(s) could not be deleted. Check the log file.',

        # Summary dialog
        'preview_result_title': 'Preview Result',
        'preview_result_text':  '{c} files will be organized.\n\nClick "Start" to begin.',
        'transfer_title':       'Transfer Complete',
        'keep_originals':       'Keep Originals',
        'delete_originals':     'Delete Originals',

        # Event dialog
        'event_dlg_title':      'Name This Event',
        'event_days':           'Selected days:',
        'event_file_count':     'Total files:',
        'event_name_lbl':       'Event name:',
        'event_placeholder':    'E.g. Ski Trip',
        'event_folder_lbl':     'Resulting folder:',
        'ok':                   'OK',
        'cancel':               'Cancel',

        # Settings dialog
        'settings_title':       'Settings',
        'theme_section':        'Theme',
        'theme_light':          'Light',
        'theme_dark':           'Dark',
        'theme_auto':           'Auto (System)',
        'lang_section':         'Language / Dil',
        'about_section':        'About',
        'about_desc':           'A desktop application that automatically archives\nphoto and video files by date and type.',
        'close':                'Close',
        'restart_note':         'Restart the application to apply language changes.',
    },
}


def set_language(lang: str) -> None:
    global _lang
    if lang in STRINGS:
        _lang = lang


def get_language() -> str:
    return _lang


def t(key: str, **kwargs) -> str:
    """Aktif dilde string döndürür. Bilinmeyen key → key kendisi."""
    text = STRINGS[_lang].get(key, STRINGS['tr'].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
