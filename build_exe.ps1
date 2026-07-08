python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-build.txt

python -m PyInstaller --noconfirm --onefile --windowed --name LotoFR --add-data "bingoloto.ico;." --icon "bingoloto.ico" app.py

Write-Host "Build terminé. Exécutable: dist/LotoFR.exe"
