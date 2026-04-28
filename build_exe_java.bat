@echo off
setlocal

javac -d out src/LotoApp.java
if errorlevel 1 exit /b 1

jar --create --file LotoFR.jar --main-class LotoApp -C out .
if errorlevel 1 exit /b 1

jpackage --input . --name LotoFR --main-jar LotoFR.jar --type exe --win-console
if errorlevel 1 exit /b 1

echo.
echo Build termine. Executable dans le dossier LotoFR\
pause
