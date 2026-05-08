import requests
from bs4 import BeautifulSoup
import re
import argparse
from urllib.parse import urljoin
import json
import os

def find_m3u8_links(url, headers):
    """Retourne une liste de liens .m3u8 sur la page donnée"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de la requête {url}: {e}")
        return [], None

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    m3u8_links = []

    for link in soup.find_all('a', href=True):
        if link['href'].lower().endswith('.m3u8'):
            full_url = urljoin(url, link['href'])
            m3u8_links.append(full_url)

    for video_tag in soup.find_all('video'):
        if video_tag.get('src') and video_tag['src'].lower().endswith('.m3u8'):
            m3u8_links.append(urljoin(url, video_tag['src']))
        for source in video_tag.find_all('source'):
            if source.get('src') and source['src'].lower().endswith('.m3u8'):
                m3u8_links.append(urljoin(url, source['src']))

    pattern = re.compile(r'https?://[^\s"\']+\.m3u8', re.IGNORECASE)
    m3u8_links += pattern.findall(html_content)

    return list(set(m3u8_links)), soup

def scan_iframes(url, headers, soup):
    """Scan des iframes pour trouver des liens .m3u8"""
    iframe_links = []
    for iframe in soup.find_all('iframe', src=True):
        iframe_url = urljoin(url, iframe['src'])
        print(f"Scan iframe: {iframe_url}")
        links, _ = find_m3u8_links(iframe_url, headers)
        if links:  # Si des liens sont trouvés dans cette iframe
            iframe_links.extend(links)
            # Retourne aussi l'URL de l'iframe pour le cache
            return iframe_links, iframe_url
    return iframe_links, None

# Arguments
parser = argparse.ArgumentParser(
    description="Scanner des liens .m3u8 sur une page web"
)
parser.add_argument("--url", help="URL d'une page web à scanner pour trouver le .m3u8")
parser.add_argument("--cache", action="store_true", help="Afficher ou utiliser le cache JSON")
parser.add_argument("--show", action="store_true", help="Afficher le contenu du cache")
args = parser.parse_args()

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

# Cas 1: URL à scanner
if args.url:
    m3u8_links, soup = find_m3u8_links(args.url, headers)
    iframe_source_url = None  # Variable pour stocker l'URL de l'iframe si trouvée

    if not m3u8_links and soup:
        print("Aucun lien direct trouvé, scan des iframes...")
        m3u8_links, iframe_source_url = scan_iframes(args.url, headers, soup)

    if m3u8_links:
        print("Liens trouvés :")
        for link in m3u8_links:
            print(link)

        # Détermine l'URL à enregistrer dans le cache
        site_url = iframe_source_url if iframe_source_url else args.url

        # Sauvegarde dans cache.json avec la structure demandée
        cache_data = {
            "site": site_url,
            "m3u8": m3u8_links
        }
        with open("cache.json", "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4, ensure_ascii=False)
        print("Liens sauvegardés dans cache.json")
    else:
        print("Aucun lien .m3u8 trouvé sur la page.")

# Cas 2: Utiliser ou afficher le cache
elif args.cache:
    if not os.path.exists("cache.json"):
        print("Le fichier cache.json n'existe pas.")
        exit()
    with open("cache.json", "r", encoding="utf-8") as f:
        cache_data = json.load(f)

    if args.show:
        print(f"Site : {cache_data.get('site', 'Inconnu')}")
        print("Liens m3u8 :")
        for link in cache_data.get("m3u8", []):
            print(link)
    else:
        print("Cache chargé, utilisez --show pour afficher les liens.")

else:
    parser.print_help()