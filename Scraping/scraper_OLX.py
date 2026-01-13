from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def scrape_olx():
    rezultate = []
    links = []
    #Keywords pentru a determina tipul tranzactiei
    vanzare_keywords = [
    "vanzare",
    "de vanzare",
    "se vinde",
    "vand",
    "vandut",     
    "cumparare",
    "achizitie",
]
    apartament_keywords = [
    "apartament",
    "ap.",
    "apt",
    "garsoniera",
    "studio",
    "penthouse",
]
    casa_keywords = [
    "casa",
    "casă",
    "vila",
    "vilă",
    "duplex",
    "triplex",
    "townhouse",
    "resedinta",
    "locuinta individuala",
]
    teren_keywords = [
    "teren",
    "parcela",
    "lot",
    "intravilan",
    "extravilan",
    "agricol",
    "constructibil",
]

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    driver.get('https://www.olx.ro/imobiliare/')
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    anunturi_olx = soup.find_all('a', class_='css-1tqlkj0')
    for a in anunturi_olx:
        href = a.get("href")
        links.append("https://www.olx.ro" + href)
    links = list(set(links))

    for link in links:
        try:
            driver.get(link)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            oras = soup.find('p', class_='css-9pna1a')
            oras = oras.text.strip() if oras else None

            judete = soup.find_all("p", class_="css-3cz5o2")
            judet = judete[1].text.strip() if len(judete) > 1 else None


            # Initialize variables to hold the extracted data
            suprafata = None
            etaj = None
            an_constructie = None
            compartimentare = None
            
            elemente = soup.find_all('p', class_='css-13x8d99')
            for element in elemente:
                text = element.text.strip()
        
                if text.startswith('Suprafata utila'):
                    suprafata_text = text.split(':', 1)[1].strip()
                    suprafata = int(''.join(c for c in suprafata_text if c in '0123456789'))
                elif text.startswith('Etaj'):
                    etaj = text.split(':',1)[1].strip()
                elif text.startswith('An constructie'):
                    an_constructie = text.split(':',1)[1].strip()
                elif text.startswith('Compartimentare'):
                    compartimentare = text.split(':',1)[1].strip()

            pret = soup.find('h3', class_='css-1j840l6')
            pret_text = pret.text
            pret = int(''.join(c for c in pret_text if c.isdigit()))
            
            tip_tranzactie_scraping = soup.find('div', class_='css-19duwlz')
            
            if tip_tranzactie_scraping:
                tip_tranzactie_text = tip_tranzactie_scraping.text.lower()
                if any(keyword in tip_tranzactie_text for keyword in vanzare_keywords):
                    tip_tranzactie = 'vanzare'
                else:
                    tip_tranzactie = 'inchiriere'
                    
            tip_imobiliar = soup.find('div', class_='css-19duwlz')
            
            tip_imobiliar_scraping = soup.find('div', class_='css-19duwlz')

            if tip_imobiliar_scraping:
                tip_imobiliar_text = tip_imobiliar_scraping.text.lower()
            else:
                tip_imobiliar_text = ""

            if any(keyword in tip_imobiliar_text for keyword in apartament_keywords):
                tip_imobiliar = "apartament"
            elif any(keyword in tip_imobiliar_text for keyword in casa_keywords):
                tip_imobiliar = "casa"
            elif any(keyword in tip_imobiliar_text for keyword in teren_keywords):
                tip_imobiliar = "teren"
            else:
                tip_imobiliar = None        
            
            
            data = datetime.today().strftime('%Y-%m-%d')
            
            processed = False
            
            id_raw = f"{oras}{judet}{pret}{data}"

        except Exception as e:
            print(f"An error occurred: {e}")
            continue
        
        rezultate.append({
            'id_raw': id_raw,
            'judet': judet,
            'oras': oras,
            'suprafata': suprafata,
            'etaj': etaj,
            'an_constructie': an_constructie,
            'compartimentare': compartimentare,
            'pret': pret,
            'tip_tranzactie': tip_tranzactie,
            'tip_imobiliar': tip_imobiliar,
            'data': data,
            'processed': processed})

        print(id_raw, judet, oras, suprafata, etaj, compartimentare, tip_tranzactie,tip_imobiliar, pret, data)

    driver.quit()
    return rezultate

# df = pd.DataFrame(rezultate)
# csv_path = os.path.join(".", "raw_data.csv")
# df.to_csv(csv_path , index=False, encoding='utf-8-sig')
# print("Scraping completed and data saved to raw_data.csv")
