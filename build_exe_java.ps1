javac -d out src/LotoApp.java
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

jar --create --file LotoFR.jar --main-class LotoApp -C out .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

jpackage --input . --name LotoFR --main-jar LotoFR.jar --type exe --win-console
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Build terminé. Exécutable dans le dossier LotoFR/"
