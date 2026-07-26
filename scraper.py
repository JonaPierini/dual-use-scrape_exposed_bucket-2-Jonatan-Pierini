import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000/home"
MAX_DEPTH = 3

def scrape():
    visited = set()
    queue = [(BASE_URL, 0)]
    buckets = []

    while queue:
        url, depth = queue.pop(0)
        if url in visited or depth > MAX_DEPTH:
            continue
        
        visited.add(url)
        print(f"Scraping {url} (Depth: {depth})")

        try:
            res = requests.get(url, timeout=5)
            text = res.text
            
            # Buscar patrones de buckets expuestos en LocalStack/S3 (puerto 4566)
            matches = re.findall(r'http://(?:localhost|127\.0\.0\.1):4566/([a-zA-Z0-9.\-_]+)', text)
            for b in matches:
                buckets.append({
                    "bucket_name": b, 
                    "endpoint": "http://localhost:4566"
                })

            # Extraer enlaces internos para seguir la profundidad hasta 3
            soup = BeautifulSoup(text, 'html.parser')
            for a in soup.find_all('a', href=True):
                next_url = urljoin(url, a['href'])
                if "localhost:8000" in next_url or "127.0.0.1:8000" in next_url:
                    queue.append((next_url, depth + 1))

        except Exception as e:
            print(f"Error en {url}: {e}")

    # Eliminar duplicados
    unique_buckets = [dict(t) for t in {tuple(d.items()) for d in buckets}]

    results = {
        "scraper": {
            "depth": MAX_DEPTH,
            "discovered_buckets": unique_buckets
        },
        "checker": {
            "buckets": []
        }
    }

    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("Scraper finalizado. results.json creado.")

if __name__ == "__main__":
    scrape()