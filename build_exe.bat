@echo off
setlocal

python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

python -m PyInstaller --noconfirm --onefile --windowed --name LotoFR --add-data "bingoloto.ico;." --icon "bingoloto.ico" app.py

echo.
echo Build termine. Executable: dist\LotoFR.exe
pause
