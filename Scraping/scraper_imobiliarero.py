from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re

def scrape_imobiliarero(url_start, tip_tranzactie):
    rezultate = []
    links = []



    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    driver.get(url_start)
    time.sleep(5) 

    soup = BeautifulSoup(driver.page_source, 'lxml')
    anunturi_imobiliare = soup.find_all('a', {'data-cy': 'listing-information-link'})
    
    for a in anunturi_imobiliare:
        href = a.get("href")
        links.append("https://www.imobiliare.ro" + href)
    links = list(set(links))

    for link in links:
        try:
            driver.get(link)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            suprafata = None
            
            nav = soup.find('nav', {'data-cy': 'breadcrumbs'})

            if nav:
                links = nav.find_all('a')
                
                text_links = [l.get_text(strip=True) for l in links if l.get_text(strip=True)]
                
                if len(text_links) >= 2:
                    raw_judet = text_links[2]
                    raw_oras = text_links[3]
                    raw_tip_imobiliar = text_links[1]
                    
                    judet = raw_judet.replace("Județul", "").strip()
                    oras = raw_oras.strip()
                    tip_imobiliar = raw_tip_imobiliar.strip()
                    
                    if "Bucure" in judet:
                        oras = f"Bucuresti, {oras}"
                        
                    print(f" Judet: {judet}, Oras: {oras}")

                
                
            suprafata = None

            label_suprafata = soup.find('span', string=re.compile(r'Suprafe|Sup\.', re.IGNORECASE))

            if not label_suprafata:
                label_suprafata = soup.find(lambda tag: tag.name == "span" and "utila" in tag.text.lower())

            if label_suprafata:
                container = label_suprafata.find_parent('div', class_='swiper-item') or label_suprafata.find_parent('div')
                
                valoare_span = container.find(lambda tag: tag.name == "span" and "mp" in tag.text.lower())
                
                if valoare_span:
                    text_suprafata = valoare_span.get_text(strip=True)
                    match = re.search(r"(\d+[\d.,]*)", text_suprafata)
                    if match:
                        try:
                            numar_str = match.group(1).replace(',', '.')
                            suprafata = round(float(numar_str))
                        except (ValueError, TypeError):
                            suprafata = "Eroare format"

            # --- Început bloc etaj ---
            label_etaj = soup.find('span', string=re.compile(r'Etaj', re.IGNORECASE))
            etaj = None # Inițializăm cu None pentru siguranță

            if label_etaj:
                container_etaj = label_etaj.find_parent('div')
                if container_etaj:
                    valoare_etaj_span = container_etaj.find('span', class_='font-semibold')
                    
                    if valoare_etaj_span:
                        text_etaj_complet = valoare_etaj_span.get_text(strip=True).lower()
                        
                        # 1. Verificăm mai întâi dacă este un etaj special (text)
                        if "parter" in text_etaj_complet:
                            etaj = "Parter"
                        elif "demisol" in text_etaj_complet:
                            etaj = "Demisol"
                        elif "mansarda" in text_etaj_complet:
                            etaj = "Mansarda"
                        else:
                            match = re.search(r'\d+', text_etaj_complet)
                            if match:
                                etaj = int(match.group())
            # --- Sfârșit bloc etaj ---

            label_an_cosntructie = soup.find('span', string=re.compile(r'An constr.', re.IGNORECASE))

            if label_an_cosntructie:
                container_an = label_an_cosntructie.find_parent('div')
                valoare_an_span = container_an.find('span', class_='font-semibold')
                
                if valoare_an_span:
                    text_raw = valoare_an_span.get_text(strip=True) 
                    
                    match = re.search(r"(\d{4})", text_raw)
                    
                    if match:
                        try:
                            an_constructie = int(match.group(1))
                        except ValueError:
                            an_constructie = None
                        
            if int(an_constructie) < 1977:
                perioada_constructie = "inainte de 1977"
            elif int(an_constructie) >= 1977 and int(an_constructie) < 1990:
                perioada_constructie = "1977-1990"
            elif int(an_constructie) >= 1990 and int(an_constructie) < 2000:
                perioada_constructie = "1990-2000"
            elif int(an_constructie) >= 2000:
                perioada_constructie = "dupa 2000"           
            
            compartimentare = None

            label_compartimentare = soup.find('section', {'data-cy': 'listing-amenities-excerpt-component'})

            if label_compartimentare:
                spans = label_compartimentare.find_all('span', class_='text-md')
                
                cuvinte_cheie = ["decomandat", "semidecomandat", "nedecomandat", "circular"]
                
                for s in spans:
                    text_span = s.get_text(strip=True).lower()

                    if any(keyword in text_span for keyword in cuvinte_cheie):
                        compartimentare = s.get_text(strip=True)
                        break 

            label_camere = soup.find('span', string=re.compile(r'Nr. cam.', re.IGNORECASE))
            if label_camere:
                container_camere = label_camere.find_parent('div')
                valoare_camere_span = container_camere.find('span', class_='font-semibold')
                
                if valoare_camere_span:
                    text_camere = valoare_camere_span.get_text(strip=True)
                    camere = text_camere.strip()
                    
                    try:
                        camere = int(camere)
                    except ValueError:
                        camere = camere

            label_pret = soup.find('div', {'aria-label':'price'})
            pret = label_pret.text
            pret = int(''.join(c for c in pret if c.isdigit()))


            platforma = "imobiliare.ro"
            
            data = datetime.today().strftime('%Y-%m-%d')

            processed = False
            
            id_raw = "".join(
                str(x) for x in [
                oras,
                judet,
                tip_imobiliar,
                suprafata,
                etaj,
                camere,
                perioada_constructie,
                tip_imobiliar,
                tip_tranzactie
            ] if x is not None
            )
                
        except Exception as e:
            print(f"Eroare la link-ul {link}: {e}")
            continue
        
        rezultate.append({
            'id_raw': id_raw,
            'URL_anunt': link,
            'judet': judet,
            'oras': oras,
            'suprafata': suprafata,
            'etaj': etaj,
            'perioada_constructie': perioada_constructie,
            'an_constructie': an_constructie,
            'compartimentare': compartimentare,
            'camere': camere,
            'pret': pret,
            'tip_tranzactie': tip_tranzactie,
            'tip_imobiliar': tip_imobiliar,
            'platforma': platforma,
            'data': data,
            'processed': processed})
        
        print(f"Anunț procesat: {link}, Oras: {oras}, Judet: {judet}, Suprafata: {suprafata}, Etaj: {etaj}, An constructie: {an_constructie}, Pret: {pret}, Tip tranzactie: {tip_tranzactie}, Tip imobiliar: {tip_imobiliar}, Platforma: {platforma}, Data: {data}, Compartimentare: {compartimentare}, Camere: {camere}, Perioada constructie: {perioada_constructie}")
    driver.quit()
    return rezultate
