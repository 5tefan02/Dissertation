from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re

def scrape_storia(url_start, tip_tranzactie, tip_imobiliar):
    rezultate = []
    links = []

    # Configurare opțiuni pentru viteză și rulare în fundal
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.page_load_strategy = 'eager' # Optimizare pentru a nu aștepta reclamele

    print("Pornire driver Selenium pentru Storia...")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    
    driver.get(url_start)
    time.sleep(5) 

    # --- 1. Extragerea link-urilor ---
    soup = BeautifulSoup(driver.page_source, 'lxml')
    anunturi_imobiliare = soup.find_all('a', {'data-cy': 'listing-item-link'})
    
    for a in anunturi_imobiliare:
        href = a.get("href")
        if href:
            links.append("https://www.storia.ro" + href)
    
    links = list(set(links))
    print(f"S-au găsit {len(links)} link-uri unice pe pagina principală.")

    # --- 2. Procesarea fiecărui link în parte ---
    for link in links:
        try:
            driver.get(link)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # INIȚIALIZARE VARIABILE CU None (Previne erorile dacă un anunț nu are anumite date)
            oras = None
            judet = None
            suprafata = None
            etaj_final = None
            an_constructie = None
            perioada_constructie = None
            camere = None
            compartimentare = None
            pret = None
            
            # --- LOCAȚIE (Oraș și Județ) ---
            location_element = soup.find('a', {'data-sentry-source-file': 'MapLink.tsx'})

            if location_element:
                text_locatie = location_element.get_text(strip=True)
                # Curățăm diacriticele
                text_locatie = text_locatie.replace('ș', 's').replace('ț', 't').replace('ă', 'a').replace('â', 'a').replace('î', 'i')
                
                parti = [p.strip() for p in text_locatie.split(',')]
                
                oras = parti[-2] if len(parti) >= 2 else parti[0]
                judet = parti[-1] if len(parti) >= 1 else None

                # Logica specială pentru București
                if "Bucuresti" in text_locatie:
                    judet = "Bucuresti"
                    sector_gasit = None
                    for p in parti:
                        if "Sector" in p:
                            sector_gasit = p
                            break
                    
                    if sector_gasit:
                        oras = f"Bucuresti, {sector_gasit}"
                    else:
                        oras = "Bucuresti"
                else:
                    if judet:
                        judet = judet.replace("Judetul", "").strip()

            # --- SUPRAFAȚĂ ---
            detalii_items = soup.find_all('div', class_=re.compile(r'e178zspo0|css-1okys8k'))
            for item in detalii_items:
                text_item = item.get_text(separator=" ", strip=True)
                if "m²" in text_item or "Suprafata" in text_item:
                    match = re.search(r"(\d+[\d.,]*)", text_item)
                    if match:
                        try:
                            numar_str = match.group(1).replace(',', '.')
                            suprafata = round(float(numar_str))
                            break
                        except:
                            continue

            # --- DETALII (Etaj, An, Camere) - O singură buclă! ---
            containere_detalii = soup.find_all('div', {'data-sentry-element': 'ItemGridContainer'})
            if not containere_detalii:
                containere_detalii = soup.find_all('div', class_=re.compile(r'css-1xw0jqp|efdvw050'))

            for container in containere_detalii:
                text_complet = container.get_text(separator=" ", strip=True).lower() 
                
                # Verificăm Etajul
                if "etaj" in text_complet or "parter" in text_complet or "demisol" in text_complet:
                    if "parter" in text_complet:
                        etaj_final = 0
                    elif "demisol" in text_complet:
                        etaj_final = "Demisol"
                    elif "mansarda" in text_complet:
                        etaj_final = "Mansarda"
                    else:
                        match = re.search(r'\d+', text_complet)
                        if match:
                            etaj_final = int(match.group())
                
                # Verificăm Anul Construcției
                elif "anul construc" in text_complet or "an construc" in text_complet:
                    match = re.search(r'\d{4}', text_complet)
                    if match:
                        an_constructie = int(match.group())
                        if an_constructie < 1977: perioada_constructie = "inainte de 1977"
                        elif 1977 <= an_constructie < 1990: perioada_constructie = "1977-1990"
                        elif 1990 <= an_constructie < 2000: perioada_constructie = "1990-2000"
                        elif an_constructie >= 2000: perioada_constructie = "dupa 2000"

                # Verificăm Camerele
                elif "camere" in text_complet:
                    match = re.search(r'\d+', text_complet)
                    if match:
                        camere = int(match.group())

            # --- COMPARTIMENTARE DIN DESCRIERE ---
            container_descriere = soup.find('div', {'data-cy': 'ad_description'})
            if not container_descriere:
                container_descriere = soup.find('div', class_='css-fl29zg')

            if container_descriere:
                text_descriere = container_descriere.get_text(separator=" ", strip=True).lower()
                
                if "semidecomandat" in text_descriere:
                    compartimentare = "semidecomandat"
                elif "nedecomandat" in text_descriere:
                    compartimentare = "nedecomandat"
                elif "decomandat" in text_descriere:
                    compartimentare = "decomandat"
                elif "circular" in text_descriere:
                    compartimentare = "circular"

            # --- EXTRAGERE PREȚ ---
            pret_element = soup.find('strong', {'data-cy': 'adPageHeaderPrice'})
            if pret_element:
                pret_text = pret_element.get_text(strip=True)
                # Extragem doar cifrele din preț
                pret = int(''.join(c for c in pret_text if c.isdigit()))
            
            # --- DATE GENERALE ---
            platforma = "Storia"
            data = datetime.today().strftime('%Y-%m-%d')
            processed = False
            
            # Generare ID Unic bazat pe datele anunțului
            id_raw = "".join(
                str(x) for x in [
                oras, judet, tip_imobiliar, suprafata, etaj_final, 
                camere, perioada_constructie, tip_imobiliar, tip_tranzactie
            ] if x is not None)
            
            
            rezultate.append({
                'id_raw': id_raw,
                'URL_anunt': link,
                'judet': judet,
                'oras': oras,
                'suprafata': suprafata,
                'etaj': etaj_final,
                'perioada_constructie': perioada_constructie,
                'an_constructie': an_constructie,
                'compartimentare': compartimentare,
                'camere': camere,
                'pret': pret,
                'tip_tranzactie': tip_tranzactie,
                'tip_imobiliar': tip_imobiliar,
                'platforma': platforma,
                'data': data,
                'processed': processed
            })
            
            print(f"Anunț procesat cu succes: {link}, ID: {id_raw}, Oras: {oras}, Judet: {judet}, Suprafata: {suprafata}, Etaj: {etaj_final}, Camere: {camere}, Pret: {pret}, Tip tranzactie: {tip_tranzactie}, Tip imobiliar: {tip_imobiliar}, Platforma: {platforma}, Data: {data}, Compartimentare: {compartimentare}, Perioada constructie: {perioada_constructie}, an_constructie: {an_constructie}")

        except Exception as e:
            print(f"Eroare la procesarea link-ului {link}: {e}")
            continue

    driver.quit()
    return rezultate