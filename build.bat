@echo off
echo PixVault - PyInstaller Build
echo ============================
pyinstaller ^
    --onefile ^
    --windowed ^
    --name PixVault ^
    --icon=images/icon.ico ^
    --add-data "images;images" ^
    --hidden-import "pymediainfo" ^
    --hidden-import "PIL._tkinter_finder" ^
    --collect-binaries "pymediainfo" ^
    --collect-data "pymediainfo" ^
    main.py
echo.
echo Build tamamlandi. dist/PixVault.exe dosyasina bakin.
pause
