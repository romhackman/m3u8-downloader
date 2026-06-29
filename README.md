```markdown
name=README.md url=https://github.com/romhackman/m3u8-downloader/blob/main/README.md
# m3u8-downloader

Outils simples pour trouver et télécharger flux vidéo HLS (.m3u8) et fichiers vidéo (mp4) via yt-dlp/ffmpeg.

Principaux scripts
- video.py — "Finder" : scanne une page (et éventuellement ses iframes) pour trouver des liens .m3u8 et les sauvegarde dans `cache.json`.
- d_m3u8.py — "Downloader" : lit `cache.json` (ou une URL directe) et lance yt-dlp pour télécharger les flux m3u8 en MP4.
- d_mp4.py — "Crawl + download" : crawler simple qui cherche des mp4 / m3u8 sur une page et utilise yt-dlp en fallback pour télécharger.
- help.py — affiche un header ASCII et des rappels d'utilisation.

Fonctionnalités
- Scanner de pages HTML et iframes pour repérer des .m3u8.
- Sauvegarde/lecture d'un cache JSON (`cache.json`) pour réutiliser les liens trouvés.
- Téléchargement avec yt-dlp + ffmpeg (option `--downloader ffmpeg`) en écrasant les fichiers existants.
- Support optionnel de `cookies.txt` si présent.
- Affichage d'une petite animation ("spinner") pendant le téléchargement.

Prérequis
- Python 3.8+ (testé avec 3.8+)
- pip
- ffmpeg (installé et accessible dans le PATH, ou adapté dans les scripts)
- yt-dlp (le script d_m3u8 recherche par défaut un binaire local `tools/yt-dlp.exe` — ou installez `yt-dlp` globalement)
- Bibliothèques Python listées dans `requirements.txt` :
  - requests
  - beautifulsoup4

Installation
1. Cloner le dépôt :
   ```bash
   git clone https://github.com/romhackman/m3u8-downloader.git
   cd m3u8-downloader
   ```

2. Installer les dépendances Python :
   ```bash
   python -m pip install -r requirements.txt
   ```

3. S'assurer que ffmpeg est installé et accessible (ex. `ffmpeg -version`).
   - Soit installez ffmpeg globalement, soit adaptez les appels dans les scripts selon votre configuration.

4. yt-dlp :
   - Placez un exécutable `yt-dlp.exe` dans le sous-dossier `tools/` (pour Windows), ou installez `yt-dlp` globalement (`pip install yt-dlp`) et modifiez `d_m3u8.py` si besoin pour utiliser le binaire système.

Utilisation

1) Trouver des liens .m3u8 sur une page (video.py)
```bash
python video.py --url "https://exemple.com/page"
```
- Si des liens sont trouvés, ils sont affichés et sauvegardés dans `cache.json` sous la forme :
```json
{
  "site": "https://exemple.com/page",
  "m3u8": [
    "https://.../playlist.m3u8",
    "https://.../alternate.m3u8"
  ]
}
```
- Si la page contient des iframes, `video.py` les scanne aussi pour trouver des m3u8.

Options utiles :
- `--cache` : charger le cache existant (`cache.json`)
- `--show` : afficher le contenu du cache après l'avoir chargé

2) Télécharger depuis le cache ou une URL directe (d_m3u8.py)
- Télécharger toutes les entrées du cache :
  ```bash
  python d_m3u8.py --download
  ```
- Télécharger et nommer le fichier :
  ```bash
  python d_m3u8.py --download --n mon_episode
  ```
  Ceci produira `mon_episode.mp4` (ou `mon_episode_2.mp4` si plusieurs liens).
- Télécharger vers un dossier personnalisé :
  ```bash
  python d_m3u8.py --download --o /chemin/vers/dossier
  ```
- Lister les .mp4 déjà téléchargés :
  ```bash
  python d_m3u8.py --ds
  ```
- Télécharger une URL m3u8 directe (mode "direct") :
  ```bash
  python d_m3u8.py --link "https://site/playlist.m3u8" --n nom_sortie
  ```

Remarques importantes pour d_m3u8.py
- Par défaut, le script cherche `tools/yt-dlp.exe` (chemin relatif au fichier). S'il n'existe pas, le script affiche une erreur et termine. Si vous utilisez `yt-dlp` installé globalement, soit placez un exécutable dans `tools/`, soit modifiez la constante `YTDLP_PATH` dans le script.
- Si `cookies.txt` est présent dans le répertoire courant, il sera automatiquement utilisé (`--cookies cookies.txt`).
- ffmpeg est utilisé comme `--downloader ffmpeg` et le script force l'option `-y` pour écraser les fichiers existants.

3) Crawler + téléchargement (d_mp4.py)
- Lancez le script et entrez l'URL de départ quand demandé :
  ```bash
  python d_mp4.py
  # puis saisissez l'URL quand le prompt apparaît
  ```
- Le script scanne la page (et les iframes) pour trouver mp4/m3u8. Si des vidéos sont détectées, il appelle `yt-dlp` en fallback pour télécharger.

Format du cache (exemple)
```json
{
  "site": "https://le-site-source.com",
  "m3u8": [
    "https://le-site-source.com/path/to/playlist.m3u8"
  ]
}
```

Dépannage
- "yt-dlp introuvable" : placer `yt-dlp.exe` dans `tools/` ou ajuster `YTDLP_PATH`.
- Erreur de ffmpeg : vérifier que `ffmpeg` est installé et accessible depuis la ligne de commande.
- Si le téléchargement échoue mais que le flux est lisible dans un navigateur, essayez d'ajouter/mettre à jour `cookies.txt` ou vérifier les headers/referer (d_m3u8 tente d'ajouter `--referer` si le cache contient un `site`).
