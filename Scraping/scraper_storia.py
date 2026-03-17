from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re

def scrape_storia(url_start, tip_tranzactie, tip_imobiliar):
    rezultate = []
    links = []

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    driver.get(url_start)
    time.sleep(5) 

    soup = BeautifulSoup(driver.page_source, 'lxml')
    anunturi_imobiliare = soup.find_all('a', {'data-cy': 'listing-item-link'})
    
    for a in anunturi_imobiliare:
        href = a.get("href")
        links.append("https://www.storia.ro" + href)
    links = list(set(links))

    for link in links:
        try:
            driver.get(link)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            location_element = soup.find('a', {'data-sentry-source-file': 'MapLink.tsx'})

            if location_element:
                text_locatie = location_element.get_text(strip=True)
                # Curățăm diacriticele pentru uniformizare (opțional, dar recomandat)
                text_locatie = text_locatie.replace('ș', 's').replace('ț', 't').replace('ă', 'a').replace('â', 'a').replace('î', 'i')
                
                # Împărțim textul în bucăți
                parti = [p.strip() for p in text_locatie.split(',')]
                
                # Inițializăm default
                oras = parti[-2] if len(parti) >= 2 else parti[0]
                judet = parti[-1] if len(parti) >= 1 else "N/A"

                # --- Logica specială pentru București ---
                # Verificăm dacă "Bucuresti" apare oriunde în textul locației
                if "Bucuresti" in text_locatie:
                    judet = "Bucuresti"
                    
                    # Căutăm care dintre părți conține cuvântul "Sector"
                    sector_gasit = None
                    for p in parti:
                        if "Sector" in p:
                            sector_gasit = p
                            break
                    
                    if sector_gasit:
                        # Dacă am găsit sectorul (ex: Sectorul 1), formatăm: Bucuresti, Sectorul 1
                        oras = f"Bucuresti, {sector_gasit}"
                    else:
                        # Dacă nu scrie sectorul (e doar cartierul), punem simplu Bucuresti
                        oras = "Bucuresti"
                
                # --- Pentru restul țării, curățăm județul ---
                else:
                    judet = judet.replace("Judetul", "").strip()
                    
            detalii_items = soup.find_all('div', class_=re.compile(r'e178zspo0|css-1okys8k'))

            suprafata = "N/A"

            for item in detalii_items:
                text_item = item.get_text(separator=" ", strip=True)
                
                # Verificăm dacă acest item se referă la suprafață
                if "m²" in text_item or "Suprafata" in text_item:
                    # Extragem doar cifrele
                    match = re.search(r"(\d+[\d.,]*)", text_item)
                    if match:
                        try:
                            numar_str = match.group(1).replace(',', '.')
                            suprafata = round(float(numar_str))
                            break # Am găsit, ieșim din loop
                        except:
                            continue
                        
                        # 1. Căutăm toate elementele de tip detaliu
            # Folosim clasa stabilă 'e178zspo0' observată în HTML-ul tău
# 1. Găsim toate containerele de detalii (grid-ul de sub titlu)
            detalii_storia = soup.find_all('div', class_=re.compile(r'e178zspo0|css-1okys8k'))

            # Inițializăm etajul cu o valoare default
            etaj_final = "N/A"

            for item in detalii_storia:
                text_complet = item.get_text(separator=" ", strip=True) # Ex: "Etaj 3" sau "Parter"
                
                # Verificăm dacă acest item conține cuvântul "Etaj" sau "Parter"
                if "Etaj" in text_complet or "Parter" in text_complet or "Demisol" in text_complet:
                    
                    # Dacă este Parter, setăm direct
                    if "Parter" in text_complet:
                        etaj_final = "Parter"
                        break
                        
                    # Dacă scrie "Etaj", extragem cifra de după el folosind Regex
                    match = re.search(r'Etaj\s*(\d+)', text_complet, re.IGNORECASE)
                    if match:
                        etaj_final = int(match.group(1))
                        break
                    
                    # Fallback: dacă nu scrie "Etaj 3", ci doar "3" într-un context de etaj
                    # (Uneori Storia are eticheta într-un div și cifra în altul)
                    match_fallback = re.search(r'\d+', text_complet)
                    if match_fallback:
                        etaj_final = int(match_fallback.group())
                        break

            # La final, variabila ta va fi etaj_final

        except Exception as e:
            print(f"Eroare la link-ul {link}: {e}")
            continue
        print(f"Anunț procesat: {link}, tranzacție: {tip_tranzactie}, tip imobiliar: {tip_imobiliar}, oraș: {oras}, județ: {judet}, suprafață: {suprafata} mp, etaj: {etaj_final}")
            # 'id_raw': id_raw,
            # 'URL_anunt': link,
            # 'judet': judet,
            # 'oras': oras,
            # 'suprafata': suprafata,
            # 'etaj': etaj,
            # 'perioada_constructie': perioada_constructie,
            # 'an_constructie': an_constructie,
            # 'compartimentare': compartimentare,
            # 'camere': camere,
            # 'pret': pret,
            # 'tip_tranzactie': tip_tranzactie,
            # 'tip_imobiliar': tip_imobiliar,
            # 'platforma': platforma,
            # 'data': data,
            # 'processed': processed})

    driver.quit()
    return rezultate