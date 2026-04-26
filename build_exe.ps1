python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

pyinstaller --noconfirm --onefile --windowed --name LotoFR app.py

Write-Host "Build terminé. Exécutable: dist/LotoFR.exe"
