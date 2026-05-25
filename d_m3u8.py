import json
import subprocess
import os
import argparse
import sys
import threading
from datetime import datetime

json_file = 'cache.json'
default_download_dir = 'downM3U8'

# Chemin vers yt-dlp local
YTDLP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'yt-dlp.exe')

def load_cache():
    if not os.path.exists(json_file):
        print(f"Le fichier {json_file} n'existe pas.")
        return []
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        print("Le JSON n'est pas valide !")
        return []

def show_cache(entries):
    for i, entry in enumerate(entries, start=1):
        print(f"{i}. {entry}")

def build_command(url, entry, output_path):
    if not os.path.exists(YTDLP_PATH):
        print(f"Erreur : yt-dlp introuvable à '{YTDLP_PATH}'")
        sys.exit(1)

    command = [
        YTDLP_PATH,
        '--user-agent',
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        '--hls-use-mpegts',
        '--downloader', 'ffmpeg',          # ← ffmpeg écrit directement le fichier final
        '--downloader-args', 'ffmpeg:-y',  # ← écrase sans demander si le fichier existe déjà
        '--no-part',                       # ← pas de fichier .part temporaire
        '-o', output_path,
    ]

    if 'm3u8' in entry and url in entry['m3u8']:
        referer = entry.get('site', 'https://le-site-source.com')
        command.extend(['--referer', referer])
    cookies_file = 'cookies.txt'
    if os.path.exists(cookies_file):
        command.extend(['--cookies', cookies_file])
    command.append(url)
    return command

def download_entries(entries, name=None, folder=None):
    download_dir = folder if folder else default_download_dir
    os.makedirs(download_dir, exist_ok=True)

    for entry in entries:
        if not isinstance(entry, dict):
            print("Entrée invalide :", entry)
            continue

        site_url = entry.get('site')
        urls_to_download = []
        if site_url:
            urls_to_download.append(site_url)
        elif 'url' in entry:
            urls_to_download.append(entry['url'])
        elif 'm3u8' in entry:
            urls_to_download.extend(entry['m3u8'])
        else:
            print("Pas d'URL trouvée pour cette entrée :", entry)
            continue

        for i, url in enumerate(urls_to_download):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            if name:
                suffix = f"_{i+1}" if len(urls_to_download) > 1 else ""
                filename = f"{name}{suffix}.mp4"
            else:
                filename = f"{timestamp}.mp4"

            output_path = os.path.join(download_dir, filename)

            print(f"\nTéléchargement : {url}")
            print(f"Destination    : {output_path}")

            command = build_command(url, entry, output_path)

            # Spinner pendant le téléchargement
            done = threading.Event()

            def spinner_fn(path):
                frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
                idx = 0
                while not done.is_set():
                    size_str = ""
                    if os.path.exists(path):
                        size = os.path.getsize(path) / (1024 * 1024)
                        size_str = f"  {size:.1f} MiB"
                    sys.stdout.write(f"\r  {frames[idx % len(frames)]} Téléchargement en cours...{size_str}   ")
                    sys.stdout.flush()
                    idx += 1
                    threading.Event().wait(0.1)

            t = threading.Thread(target=spinner_fn, args=(output_path,), daemon=True)
            t.start()

            try:
                result = subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                done.set()
                t.join()
                size = os.path.getsize(output_path) / (1024 * 1024)
                sys.stdout.write(f"\r  ✔ Terminé : {output_path}  ({size:.1f} MiB)\n")
                sys.stdout.flush()
            except subprocess.CalledProcessError as e:
                done.set()
                t.join()
                sys.stdout.write(f"\r  ✘ Erreur pour {url} : {e}\n")
                sys.stdout.flush()

def list_downloaded_files(folder=None):
    target_dir = folder if folder else default_download_dir
    if not os.path.exists(target_dir):
        print(f"Aucun dossier '{target_dir}' trouvé.")
        return
    files = [f for f in os.listdir(target_dir) if f.endswith('.mp4')]
    if not files:
        print(f"Aucun fichier .mp4 dans '{target_dir}'.")
        return
    print(f"Fichiers téléchargés dans '{target_dir}' :")
    for f in sorted(files):
        print(f"  - {os.path.join(target_dir, f)}")

# ── Parser ────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(
    prog='d_m3u8r.py',
    description="Téléchargeur yt-dlp avec gestion d'un cache JSON.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
exemples :
  python d_m3u8.py --show
      Affiche le contenu du cache JSON.

  python d_m3u8.py --download
      Télécharge toutes les entrées du cache dans ./downM3U8/

  python d_m3u8.py --download --n ma_video
      Télécharge et nomme le fichier ma_video.mp4

  python d_m3u8.py --download --o /tmp/videos
      Télécharge dans /tmp/videos/ au lieu de downM3U8/

  python d_m3u8.py --download --n episode1 --o /tmp/series
      Télécharge episode1.mp4 dans /tmp/series/

  python d_m3u8.py --ds
      Liste les .mp4 présents dans ./downM3U8/

  python d_m3u8.py --ds --o /tmp/videos
      Liste les .mp4 dans /tmp/videos/
"""
)

parser.add_argument('--show', action='store_true',
    help='Afficher le contenu du cache JSON (cache.json)')
parser.add_argument('--download', action='store_true',
    help='Télécharger les fichiers listés dans le cache JSON')
parser.add_argument('--n', type=str, metavar='NOM',
    help='Nom du fichier de sortie sans extension (ex: ma_video → ma_video.mp4)')
parser.add_argument('--o', type=str, metavar='DOSSIER',
    help=f'Dossier de téléchargement (défaut : {default_download_dir})')
parser.add_argument('--ds', action='store_true',
    help='Lister les fichiers .mp4 déjà téléchargés dans le dossier cible')
parser.add_argument('--link', type=str,
    help='URL m3u8 directe à télécharger (ex: https://site/playlist.m3u8)')

args = parser.parse_args()
entries = load_cache()

if args.link:
    # mode direct m3u8
    fake_entry = {
        "m3u8": [args.link]
    }
    download_entries([fake_entry], name=args.n, folder=args.o)

else:
    # mode cache JSON
    if args.show:
        show_cache(entries)

    if args.download:
        download_entries(entries, name=args.n, folder=args.o)

    if args.ds:
        list_downloaded_files(folder=args.o)

    if not any([args.show, args.download, args.ds]):
        parser.print_help()