"""
Web Crawler Éducatif
====================
Ce script montre comment construire un crawler web simple et respectueux.

IMPORTANT - Éthique du crawling:
1. Toujours respecter le fichier robots.txt
2. Limiter la vitesse des requêtes (rate limiting)
3. Ne crawler que des sites pour lesquels vous avez la permission
4. Identifier votre bot avec un User-Agent approprié
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import re


class SimpleCrawler:
    """Crawler web simple et éducatif"""
    
    def __init__(self, start_url, max_pages=10, delay=1):
        """
        Args:
            start_url: URL de départ
            max_pages: Nombre maximum de pages à crawler
            delay: Délai entre chaque requête (en secondes)
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = delay
        self.visited = set()
        self.to_visit = deque([start_url])
        self.domain = urlparse(start_url).netloc
        
        # User-Agent poli et identifiable
        self.headers = {
            'User-Agent': 'EducationalCrawler/1.0 (Educational purposes)'
        }
    
    def is_valid_url(self, url):
        """Vérifie si l'URL est valide et appartient au même domaine"""
        parsed = urlparse(url)
        return (
            bool(parsed.netloc) and 
            bool(parsed.scheme) and
            parsed.netloc == self.domain
        )
    
    def get_links(self, url, html):
        """Extrait tous les liens d'une page"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convertir en URL absolue
            absolute_url = urljoin(url, href)
            
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)
        
        return links
    
    def extract_text(self, html):
        """Extrait le texte principal de la page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Supprimer scripts et styles
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Extraire le texte
        text = soup.get_text()
        # Nettoyer les espaces multiples
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def crawl(self):
        """Lance le crawling"""
        print(f"🕷️  Début du crawling de: {self.start_url}")
        print(f"📊 Limite: {self.max_pages} pages\n")
        
        pages_data = []
        
        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.popleft()
            
            # Éviter de visiter deux fois la même URL
            if url in self.visited:
                continue
            
            try:
                print(f"📄 [{len(self.visited) + 1}/{self.max_pages}] Crawling: {url}")
                
                # Respecter le délai entre les requêtes
                if self.visited:
                    time.sleep(self.delay)
                
                # Récupérer la page
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                # Marquer comme visitée
                self.visited.add(url)
                
                # Extraire les données
                html = response.text
                text = self.extract_text(html)
                links = self.get_links(url, html)
                
                # Sauvegarder les données
                pages_data.append({
                    'url': url,
                    'title': BeautifulSoup(html, 'html.parser').title.string if BeautifulSoup(html, 'html.parser').title else 'No title',
                    'text_length': len(text),
                    'links_found': len(links)
                })
                
                # Ajouter les nouveaux liens à visiter
                for link in links:
                    if link not in self.visited and link not in self.to_visit:
                        self.to_visit.append(link)
                
                print(f"   ✓ Trouvé {len(links)} liens | Texte: {len(text)} caractères")
                
            except requests.RequestException as e:
                print(f"   ✗ Erreur: {e}")
            except Exception as e:
                print(f"   ✗ Erreur inattendue: {e}")
        
        print(f"\n✅ Crawling terminé!")
        print(f"📊 Pages visitées: {len(self.visited)}")
        print(f"📋 Pages en attente: {len(self.to_visit)}")
        
        return pages_data


class RobotsTxtChecker:
    """Vérifie si le crawling est autorisé selon robots.txt"""
    
    @staticmethod
    def can_fetch(url, user_agent='*'):
        """Vérifie si l'URL peut être crawlée selon robots.txt"""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        try:
            response = requests.get(robots_url, timeout=5)
            if response.status_code == 200:
                print(f"\n📜 robots.txt trouvé à {robots_url}")
                print("Première lignes:")
                print(response.text[:500])
                return True
            else:
                print(f"\n📜 Pas de robots.txt (status: {response.status_code})")
                return True
        except requests.RequestException:
            print(f"\n📜 Impossible d'accéder à robots.txt")
            return True


# ============================================================================
# EXEMPLES D'UTILISATION
# ============================================================================

def exemple_1_crawl_basique():
    """Exemple 1: Crawl basique d'un site"""
    print("=" * 70)
    print("EXEMPLE 1: Crawl basique")
    print("=" * 70)
    
    # Site d'exemple (remplacer par un site que vous avez la permission de crawler)
    url = "https://example.com"
    
    # Vérifier robots.txt
    RobotsTxtChecker.can_fetch(url)
    
    # Créer et lancer le crawler
    crawler = SimpleCrawler(
        start_url=url,
        max_pages=5,
        delay=1  # 1 seconde entre chaque requête
    )
    
    data = crawler.crawl()
    
    # Afficher les résultats
    print("\n📊 RÉSULTATS:")
    for i, page in enumerate(data, 1):
        print(f"\n{i}. {page['title']}")
        print(f"   URL: {page['url']}")
        print(f"   Texte: {page['text_length']} caractères")
        print(f"   Liens: {page['links_found']}")


def exemple_2_extraction_specifique():
    """Exemple 2: Extraction d'informations spécifiques"""
    print("\n" + "=" * 70)
    print("EXEMPLE 2: Extraction d'informations spécifiques")
    print("=" * 70)
    
    url = "https://example.com"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraire tous les titres
        print("\n📌 TITRES (h1, h2, h3):")
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3']), 1):
            print(f"{i}. [{heading.name}] {heading.get_text().strip()}")
        
        # Extraire tous les liens
        print("\n🔗 LIENS:")
        for i, link in enumerate(soup.find_all('a', href=True)[:10], 1):
            print(f"{i}. {link.get_text().strip()[:50]} -> {link['href']}")
        
        # Extraire les images
        print("\n🖼️  IMAGES:")
        for i, img in enumerate(soup.find_all('img')[:5], 1):
            print(f"{i}. {img.get('alt', 'No alt')} -> {img.get('src', 'No src')}")
            
    except Exception as e:
        print(f"Erreur: {e}")


def exemple_3_sitemap_generator():
    """Exemple 3: Générer un sitemap simple"""
    print("\n" + "=" * 70)
    print("EXEMPLE 3: Générateur de sitemap")
    print("=" * 70)
    
    url = "https://example.com"
    crawler = SimpleCrawler(start_url=url, max_pages=10, delay=1)
    data = crawler.crawl()
    
    # Générer un sitemap simple
    sitemap = "SITEMAP\n" + "=" * 50 + "\n\n"
    for page in data:
        sitemap += f"• {page['title']}\n"
        sitemap += f"  {page['url']}\n\n"
    
    print(sitemap)
    
    # Sauvegarder dans un fichier
    with open('/home/claude/sitemap.txt', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print("💾 Sitemap sauvegardé dans sitemap.txt")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║         WEB CRAWLER ÉDUCATIF - GUIDE D'UTILISATION             ║
╚════════════════════════════════════════════════════════════════╝

⚠️  RAPPEL IMPORTANT:
   • Ne crawlez que des sites pour lesquels vous avez la permission
   • Respectez toujours le fichier robots.txt
   • Utilisez des délais raisonnables entre les requêtes
   • Identifiez votre crawler avec un User-Agent approprié

📚 Ce script contient 3 exemples:
   1. Crawl basique d'un site
   2. Extraction d'informations spécifiques
   3. Génération d'un sitemap

Décommentez l'exemple que vous souhaitez exécuter ci-dessous:
""")
    
    # Décommentez l'exemple que vous voulez tester:
    # exemple_1_crawl_basique()
    # exemple_2_extraction_specifique()
    # exemple_3_sitemap_generator()
    
    print("\n💡 Pour utiliser ce script:")
    print("   1. Installez les dépendances: pip install requests beautifulsoup4")
    print("   2. Décommentez un exemple dans la section __main__")
    print("   3. Remplacez l'URL par un site que vous pouvez crawler légalement")
    print("   4. Exécutez: python web_crawler_educatif.py")
