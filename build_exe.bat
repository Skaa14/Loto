@echo off
setlocal

python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

pyinstaller --noconfirm --onefile --windowed --name LotoFR app.py

echo.
echo Build termine. Executable: dist\LotoFR.exe
pause
