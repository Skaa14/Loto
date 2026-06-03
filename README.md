# LotoFR (1 à 90)

<p align="center">
  <img src="bingoloto.ico" width="100" height="100" alt="BingoLoto Logo">
  <br>
  <b>Application desktop moderne pour animer vos lotos.</b>
  <br><br>
  <a href="https://github.com/Skaa14/Loto/releases/latest">
    <img src="https://img.shields.io/badge/TÉLÉCHARGER-LotoFR_Windows-blue?style=for-the-badge&logo=windows" alt="Télécharger LotoFR">
  </a>
</p>

---

LotoFR est une application complète pour animer un loto français (1 à 90), incluant une gestion de thèmes, un historique stylisé et un tirage aléatoire avec suspense.

## Fonctionnalités

- **Double Thème** : Support complet du mode Sombre (Dark) et Clair (Light) pour s'adapter à toutes les ambiances.
- Blocage strict des doublons.
- Bouton **Reset**.
- Affichage des 3 derniers numéros avec tailles différentes.
- **Historique Premium** : Affichage agrandi et stylisé des numéros tirés sous forme de flux dynamique.
- **Grille Interactive** : Visualisation 1..90 avec coloration intégrale des blocs de numéros tirés (vert pour les anciens, doré pour le dernier).
- **Tirage avec Suspense** : Animation de ~3.5s avec ralentissement exponentiel (easing) avant l'arrêt sur le numéro final.
- Verrouillage des interactions pendant l'animation.
- Boutons d'annonce: **Quine simple**, **Quine double**, **Carton plein**.
- Interface responsive (fenêtre redimensionnable), lisible pour écran/TV.

## Lancer en mode développement

Prérequis: Python 3.9+ et la bibliothèque PySide6.

```bash
python -m pip install -r requirements.txt
python app.py
```

## Générer le `.exe` autonome (Windows)

### Option 1 (double-clic)

- Lancer `build_exe.bat` (cmd)
- ou `build_exe.ps1` (PowerShell)

### Option 2 (ligne de commande)

```bash
python -m pip install --upgrade pip
python -m pip install pyside6 pyinstaller
pyinstaller --noconfirm --onefile --windowed --name LotoFR app.py
```

Le binaire final sera généré ici:

- `dist/LotoFR.exe`

## Notes

- Le `.exe` produit par PyInstaller avec `--onefile` est autonome côté utilisateur final.
- Aucune dépendance serveur: application 100% locale.
