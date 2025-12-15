from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

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
                suprafata = text.split(':',1)[1].strip()
            elif text.startswith('Etaj'):
                etaj = text.split(':',1)[1].strip()
            elif text.startswith('An constructie'):
                an_constructie = text.split(':',1)[1].strip()
            elif text.startswith('Compartimentare'):
                compartimentare = text.split(':',1)[1].strip()

        pret = soup.find('h3', class_='css-1j840l6')
        pret = pret.text.strip() if pret else None

    except Exception as e:
        print(f"An error occurred: {e}")
        continue
    
    rezultate.append({
        'judet': judet,
        'oras': oras,
        'suprafata': suprafata,
        'etaj': etaj,
        'an_constructie': an_constructie,
        'pret': pret})

    print(judet, oras, suprafata, etaj, pret)

driver.quit()

df = pd.DataFrame(rezultate)
csv_path = os.path.join(".", "raw_data.csv")
df.to_csv(csv_path , index=False, encoding='utf-8-sig')
print("Scraping completed and data saved to raw_data.csv")
