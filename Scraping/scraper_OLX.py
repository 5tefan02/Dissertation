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
            
            data = datetime.today().strftime('%Y-%m-%d')
            
            id = f"{oras}{judet}{pret}{data}"

        except Exception as e:
            print(f"An error occurred: {e}")
            continue
        
        rezultate.append({
            'id': id,
            'judet': judet,
            'oras': oras,
            'suprafata': suprafata,
            'etaj': etaj,
            'an_constructie': an_constructie,
            'compartimentare': compartimentare,
            'pret': pret,
            'data': data})

        print(id, judet, oras, suprafata, etaj, compartimentare, pret, data)

    driver.quit()
    return rezultate

# df = pd.DataFrame(rezultate)
# csv_path = os.path.join(".", "raw_data.csv")
# df.to_csv(csv_path , index=False, encoding='utf-8-sig')
# print("Scraping completed and data saved to raw_data.csv")
