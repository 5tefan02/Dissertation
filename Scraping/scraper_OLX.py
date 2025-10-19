import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

rezultate = []
links = []
# Scraper pentru preturile anunturilor de pe OLX
html_text = requests.get('https://www.olx.ro/imobiliare/').text
soup = BeautifulSoup(html_text, 'lxml')
anunturi_olx = soup.find_all('a', class_='css-1tqlkj0')
for a in anunturi_olx:
    href = a.get("href")
    links.append("https://www.olx.ro" + href)

for link in links:
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        
        oras = soup.find('p', class_='css-9pna1a').text.strip()
        
        judet = soup.find("p", class_="3cz5o2")
        elemente = soup.find_all('p', class_='css-13x8d99')

        # Initialize variables to hold the extracted data
        suprafata = None
        etaj = None
        an_constructie = None
        compartimentare = None
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

        pret = soup.find('h3', class_='css-1j840l6').text.strip()
    
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
    
df = pd.DataFrame(rezultate)
csv_path = os.path.join(".", "Data", "raw_data.csv")
df.to_csv(csv_path , index=False, encoding='utf-8-sig')
print("Scraping completed and data saved to raw_data.csv")
 