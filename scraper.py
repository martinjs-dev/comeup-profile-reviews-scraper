import asyncio
import json
import os
import argparse
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urljoin

class ComeUpScraper:
    def __init__(self, profile_url):
        self.profile_url = profile_url
        self.results = []
        
    async def start(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1366, "height": 768})
            page = await context.new_page()
            
            # Récupération des services
            services = await self.get_services(page)
            if not services:
                print("🚫 Aucun service trouvé. Fin du script.")
                await browser.close()
                return
            
            # Dédoublonnage
            unique_services = list(dict.fromkeys(services))
            print(f"\n🔍 {len(unique_services)} services uniques trouvés")
            
            # Récupération des avis pour chaque service
            for service_url in unique_services:
                reviews = await self.get_reviews(page, service_url)
                self.results.extend(reviews)
                print(f"Total des avis jusqu'à présent: {len(self.results)}")
            
            # Sauvegarde des résultats
            self.save_results()
            
            await browser.close()
    
    async def get_services(self, page):
        print(f"\n🔍 Récupération des services depuis : {self.profile_url}")
        try:
            await page.goto(self.profile_url, timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            service_links = await page.query_selector_all("a.service-title[href*='/fr/service/']")
            
            if not service_links:
                print("❌ Aucun service trouvé.")
                return []
            
            services = []
            for link in service_links:
                href = await link.get_attribute("href")
                full_url = urljoin("https://comeup.com", href)
                services.append(full_url)
                print(f"- Service trouvé : {full_url}")
            
            return services
            
        except Exception as e:
            print(f"❌ Aucun service trouvé ou erreur : ", e)
            return []
    
    async def get_reviews(self, page, service_url):
        print(f"\n📝 Scraping des avis pour : {service_url}")
        reviews_list = []
        
        try:
            await page.goto(service_url, timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            # Scroller jusqu'à la section des avis
            try:
                await page.evaluate("window.scrollTo(0, document.querySelector('#reviews--all').offsetTop);")
                await page.wait_for_timeout(1000)
            except:
                print("⚠️ Impossible de scroller jusqu'aux avis")
            
            # Cliquer sur "Plus de commentaires" jusqu'à ce qu'il n'y en ait plus
            while True:
                try:
                    more_button = await page.query_selector("button.btn.btn-primary:has-text('Plus de commentaires')")
                    if not more_button or not await more_button.is_visible():
                        break
                    
                    print("Clic sur Plus de commentaires...")
                    await more_button.click()
                    await page.wait_for_timeout(2000)
                except Exception as e:
                    print(f"⚠️ Arrêt du chargement: {str(e)}")
                    break
            
            # Extraction directe du HTML pour une analyse plus précise
            html_content = await page.content()
            
            # Maintenant, faire une analyse manuelle du HTML
            await page.evaluate("""
            () => {
                window.allReviews = [];
                document.querySelectorAll('div.review[data-review-id][data-cy="review"]').forEach(reviewElem => {
                    // Vérifier si c'est la réponse du vendeur
                    const isSellerReply = reviewElem.querySelector('.reviewTitle')?.textContent.trim() === 'Martin_JS';
                    if (isSellerReply) return;
                    
                    // Extraire les données de l'avis client
                    const reviewId = reviewElem.getAttribute('data-review-id');
                    const clientName = reviewElem.querySelector('.reviewTitle')?.textContent.trim() || 'Inconnu';
                    const commentText = reviewElem.querySelector('.reviewBody')?.textContent.trim() || '';
                    const dateText = reviewElem.querySelector('time')?.textContent.trim() || '';
                    const hasThumbsUp = !!reviewElem.querySelector('.fillGreen500');
                    
                    // Chercher la réponse du vendeur (élément suivant avec Martin_JS)
                    let sellerResponseElem = reviewElem.querySelector('div.review div.review');
                    let sellerResponse = null;
                    if (sellerResponseElem && sellerResponseElem.querySelector('.reviewTitle')?.textContent.trim() === 'Martin_JS') {
                        sellerResponse = sellerResponseElem.querySelector('.reviewBody')?.textContent.trim() || null;
                    }
                    
                    window.allReviews.push({
                        reviewId,
                        clientName,
                        commentText,
                        dateText,
                        hasThumbsUp,
                        sellerResponse
                    });
                });
                
                return window.allReviews.length;
            }
            """)
            
            # Récupérer les résultats de l'analyse JavaScript
            reviews_data = await page.evaluate("window.allReviews")
            
            print(f"Trouvé {len(reviews_data)} avis sur cette page")
            
            # Extraire le titre du service
            service_name = await page.title()
            service_name = service_name.split(" | ")[0] if " | " in service_name else service_name
            
            # Convertir en format de sortie
            for review in reviews_data:
                reviews_list.append({
                    "service_url": service_url,
                    "service_name": service_name,
                    "client": review.get("clientName", "Inconnu"),
                    "commentaire": review.get("commentText", ""),
                    "date": review.get("dateText", ""),
                    "positive": review.get("hasThumbsUp", False),
                    "seller_response": review.get("sellerResponse", "")
                })
                print(f"✅ Avis de {review.get('clientName', 'Inconnu')} récupéré")
            
        except Exception as e:
            print(f"⚠️ Erreur lors du scraping des avis : {str(e)}")
        
        return reviews_list
    
    def save_results(self):
        if not self.results:
            print("\n📭 Aucun avis trouvé sur les services.")
            return
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)
        
        # Sauvegarde en JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"data/avis_comeup_{timestamp}.json"
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 {len(self.results)} avis sauvegardés dans {json_filename}")
        
        # Sauvegarde en CSV si pandas est disponible
        try:
            import pandas as pd
            csv_filename = f"data/avis_comeup_{timestamp}.csv"
            df = pd.DataFrame(self.results)
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"💾 CSV également sauvegardé dans {csv_filename}")
        except ImportError:
            print("⚠️ Pandas non disponible, pas de sauvegarde CSV")


async def main():
    # Configurer le parseur d'arguments
    parser = argparse.ArgumentParser(description='Scraper les avis depuis un profil ComeUp.')
    parser.add_argument('--url', '-u', type=str, 
                        help='URL du profil ComeUp (ex: https://comeup.com/fr/@username)',
                        default="https://comeup.com/fr/@defaultusername/")
    
    # Parser les arguments
    args = parser.parse_args()
    profile_url = args.url
    
    print(f"Démarrage du scraping pour le profil: {profile_url}")
    scraper = ComeUpScraper(profile_url)
    await scraper.start()

if __name__ == "__main__":
    asyncio.run(main())