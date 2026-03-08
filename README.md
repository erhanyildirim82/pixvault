# PixVault

> **Automatic photo & video archiver for Windows**
> Organizes your media files by date, device, and source — with duplicate detection.

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Platform](https://img.shields.io/badge/platform-Windows-lightgrey) ![Python](https://img.shields.io/badge/python-3.11%2B-green)

---

## English

### What is PixVault?

PixVault is a Windows desktop application that automatically organizes your photos and videos into a clean, date-based archive. It reads EXIF and video metadata to determine the actual capture date, detects duplicate files, recognizes media from WhatsApp and Telegram, and separates files by camera brand — all without touching your originals until you explicitly confirm.

### Features

| Feature | Description |
|---|---|
| Date-based organization | Creates `YYYY / YYYY-MM MonthName` folder hierarchy |
| Camera brand detection | Separates folders by device: `Photos (iPhone)`, `Photos (Samsung)`, `Photos (Nikon)`, etc. |
| Duplicate detection | MD5 hash comparison — duplicates go to a `Duplicates` folder |
| WhatsApp / Telegram | Automatically routed to their own subfolder within the correct month |
| Social media photos | Files with no camera EXIF (Make/Model stripped) go to `Social Media` |
| Event grouping | Select date ranges and name them as events (e.g. "Ski Trip 2024") |
| Safe move mode | Files are **copied first**, then a confirmation dialog asks before deleting originals |
| Preview (dry run) | See the full reorganization plan before any file is touched |
| Light / Dark theme | Follows the system theme or can be set manually |
| Bilingual UI | Turkish and English — change in Settings |

### Folder Structure

After archiving, your target directory will look like this:

```
Archive/
├── 2024/
│   ├── 2024-08 August/
│   │   ├── Photos (iPhone)/
│   │   ├── Photos (Samsung)/
│   │   ├── Photos/              ← no brand info available
│   │   ├── Videos (iPhone)/
│   │   ├── WhatsApp/            ← WA media for that month
│   │   └── Telegram/
│   └── 2024-12 December/
│       └── ...
├── Duplicates/
├── No Date/
│   ├── Photos/
│   └── WhatsApp/
└── pixvault_log_YYYY-MM-DD.txt
```

### How WhatsApp Detection Works

PixVault uses a three-tier detection system:

1. **Folder name** — parent folder contains "whatsapp" or "telegram"
2. **File name pattern** — matches `-WA0001.` suffix or `WhatsApp ` prefix
3. **EXIF analysis** — WhatsApp strips camera Make/Model fields; files with no camera info are classified as `Social Media`

This also handles the tricky case of iPhone-saved WhatsApp photos that get renamed to `IMG_XXXX.JPG`.

### Supported Formats

| Photos | Videos |
|---|---|
| JPG, JPEG, PNG, HEIC, HEIF | MP4, MOV, AVI, MKV, M4V |
| RAW, CR2, CR3, NEF, ARW, DNG | 3GP, WMV |
| TIFF, BMP | |

### Installation & Usage

**Requirements:** Windows 10/11.

> **MediaInfo** is bundled inside the `.exe` — no separate installation needed.
> If PixVault shows a "MediaInfo not found" warning at startup, install it manually from
> [mediaarea.net/en/MediaInfo/Download/Windows](https://mediaarea.net/en/MediaInfo/Download/Windows)
> and restart PixVault. Without MediaInfo, video date detection is disabled (photos are unaffected).

1. Download `PixVault.exe` from the [Releases](https://github.com/erhanyildirim82/pixvault/releases) page
2. Double-click to launch (no installation required)
3. Select **Source Folder** (where your photos are)
4. Select **Target / Archive Folder** (where the organized archive will be created)
5. Click **Scan** — review the file list and statistics
6. Optionally group selected days as named **Events**
7. Choose **Copy** or **Move**, then click **Start**

> ⚠ **Move mode** copies files first, then asks for confirmation before deleting originals. The default button is "Keep Originals" — deletion requires an explicit click.

### Building from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python main.py

# Build .exe
build.bat
```

**requirements.txt**
```
PyQt6
Pillow
piexif
pymediainfo
pyinstaller
```

### Version History

| Version | Date | Notes |
|---|---|---|
| v1.0.0 | 2026-03 | Initial stable release |

---

## Türkçe

### PixVault Nedir?

PixVault, fotoğraf ve video dosyalarınızı otomatik olarak düzenli bir arşive aktaran Windows masaüstü uygulamasıdır. Dosyaların çekilme tarihini EXIF ve video metadata'sından okur, duplikat dosyaları tespit eder, WhatsApp ve Telegram'dan gelen medyayı otomatik ayırır, kamera markasına göre klasör oluşturur — ve siz onaylayana kadar orijinal dosyalara dokunmaz.

### Özellikler

| Özellik | Açıklama |
|---|---|
| Tarih bazlı düzenleme | `YYYY / YYYY-MM AyAdı` klasör yapısı oluşturur |
| Kamera markası tespiti | `Fotoğraflar (iPhone)`, `Fotoğraflar (Samsung)`, `Fotoğraflar (Nikon)` gibi ayrı klasörler |
| Duplikat tespiti | MD5 hash karşılaştırması — tekrar eden dosyalar `Tekrarlar` klasörüne ayrılır |
| WhatsApp / Telegram | İlgili ay klasörü içinde kendi alt klasörüne otomatik yönlendirilir |
| Sosyal medya fotoğrafları | EXIF kamera bilgisi silinmiş dosyalar `Sosyal Medya` klasörüne gider |
| Etkinlik gruplama | Tarih aralığı seçip "Kayak Tatili 2024" gibi etkinlik adı verebilirsiniz |
| Güvenli taşıma modu | Dosyalar **önce kopyalanır**, ardından onaylı silme dialogu açılır |
| Ön izleme | Hiçbir dosyaya dokunulmadan tüm düzenleme planını görebilirsiniz |
| Açık / Koyu tema | Sistem temasını takip eder veya elle ayarlanabilir |
| İki dil desteği | Türkçe ve İngilizce — Ayarlar'dan değiştirilebilir |

### Klasör Yapısı

Arşivleme sonrası hedef klasörünüz şu şekilde görünür:

```
Arşiv/
├── 2024/
│   ├── 2024-08 Ağustos/
│   │   ├── Fotoğraflar (iPhone)/
│   │   ├── Fotoğraflar (Samsung)/
│   │   ├── Fotoğraflar/         ← marka bilgisi yoksa
│   │   ├── Videolar (iPhone)/
│   │   ├── WhatsApp/            ← o aya ait WA dosyaları
│   │   └── Telegram/
│   └── 2024-12 Aralık/
│       └── ...
├── Tekrarlar/
├── Tarihsiz/
│   ├── Fotoğraflar/
│   └── WhatsApp/
└── pixvault_log_YYYY-MM-DD.txt
```

### WhatsApp Tespiti Nasıl Çalışır?

PixVault üç aşamalı bir tespit sistemi kullanır:

1. **Klasör adı** — üst klasör adında "whatsapp" veya "telegram" geçiyorsa
2. **Dosya adı deseni** — `-WA0001.` son eki veya `WhatsApp ` ön eki
3. **EXIF analizi** — WhatsApp Make/Model alanlarını siliyor; kamera bilgisi olmayan dosyalar `Sosyal Medya` olarak sınıflandırılır

Bu yöntem, iPhone'un WhatsApp fotoğraflarını `IMG_XXXX.JPG` olarak yeniden adlandırdığı zor durumu da kapsar.

### Desteklenen Formatlar

| Fotoğraf | Video |
|---|---|
| JPG, JPEG, PNG, HEIC, HEIF | MP4, MOV, AVI, MKV, M4V |
| RAW, CR2, CR3, NEF, ARW, DNG | 3GP, WMV |
| TIFF, BMP | |

### Kurulum ve Kullanım

**Gereksinimler:** Windows 10/11.

> **MediaInfo** `.exe` dosyasının içine gömülüdür — ayrıca kurulum gerekmez.
> Başlangıçta "MediaInfo Bulunamadı" uyarısı çıkarsa
> [mediaarea.net/en/MediaInfo/Download/Windows](https://mediaarea.net/en/MediaInfo/Download/Windows)
> adresinden manuel olarak kurup PixVault'u yeniden başlatın.
> MediaInfo olmadan video tarih tespiti devre dışı kalır (fotoğraflar etkilenmez).

1. [Releases](https://github.com/erhanyildirim82/pixvault/releases) sayfasından `PixVault.exe` indirin
2. Çift tıklayarak başlatın (kurulum gerekmez)
3. **Kaynak Klasör**'ü seçin (fotoğraflarınızın bulunduğu yer)
4. **Hedef / Arşiv Klasörü**'nü seçin (düzenlenmiş arşivin oluşturulacağı yer)
5. **Tara**'ya tıklayın — dosya listesini ve istatistikleri inceleyin
6. İsterseniz seçili günleri **Etkinlik** olarak adlandırın
7. **Kopyala** veya **Taşı** seçip **Başlat**'a tıklayın

> ⚠ **Taşı modu**, dosyaları önce kopyalar; ardından orijinalleri silmeden önce onay dialogu açar. Varsayılan buton "Şimdi Silme"dir — silme işlemi için açıkça tıklanması gerekir.

### Kaynak Koddan Derleme

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Doğrudan çalıştır
python main.py

# .exe derle
build.bat
```

### Sürüm Geçmişi

| Sürüm | Tarih | Notlar |
|---|---|---|
| v1.0.0 | 2026-03 | İlk kararlı sürüm |

---

*Developed by [Erhan/Dev](https://github.com/erhanyildirim82)*
