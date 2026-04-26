# LotoFR (1 à 90)

Application desktop autonome pour animer un loto français (bingo 1 à 90), avec interface moderne, historique en temps réel et tirage aléatoire animé.

## Fonctionnalités

- Ajout manuel d'un numéro (1 à 90) avec validation stricte.
- Touche **Entrée** pour ajouter rapidement le numéro saisi.
- Blocage strict des doublons.
- Bouton **Reset**.
- Affichage des 3 derniers numéros avec tailles différentes.
- Historique complet des tirages, mis à jour en temps réel.
- Grille complète 1..90 (10 colonnes), coloration immédiate des numéros tirés.
- Tirage aléatoire avec animation ~3.5s et ralentissement progressif.
- Verrouillage des interactions pendant l'animation.
- Boutons d'annonce: **Quine simple**, **Quine double**, **Carton plein**.
- Interface responsive (fenêtre redimensionnable), lisible pour écran/TV.

## Lancer en mode développement

Prérequis: Python 3.11+.

```bash
python app.py
```

## Générer le `.exe` autonome (Windows)

### Option 1 (double-clic)

- Lancer `build_exe.bat` (cmd)
- ou `build_exe.ps1` (PowerShell)

### Option 2 (ligne de commande)

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
pyinstaller --noconfirm --onefile --windowed --name LotoFR app.py
```

Le binaire final sera généré ici:

- `dist/LotoFR.exe`

## Notes

- Le `.exe` produit par PyInstaller avec `--onefile` est autonome côté utilisateur final.
- Aucune dépendance serveur: application 100% locale.
