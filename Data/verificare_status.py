from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Data.cleaner import clean_price


def verificare_status(driver, url, platforma):
    try:
        driver.get(url)

        # OLX
        if platforma == "OLX":
            try:
                WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="ad-price-container"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="500-page"]'))
                    )
                )
            except:
                pass

            soup = BeautifulSoup(driver.page_source, 'lxml')

            if soup.find('p', {'data-cy': '500-page'}):
                print(f"[Inactiv - OLX] Pagina de eroare detectata: {url}")
                return None

            pret_element = soup.find(attrs={'data-testid': 'ad-price-container'})

        # IMOBILIARE.RO
        elif platforma == "imobiliare.ro":
            time.sleep(2)

            if driver.current_url != url:
                print(f"[Inactiv - imobiliare.ro] Redirect detectat: {url}")
                return None

            try:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="price"]'))
                )
            except:
                pass

            soup = BeautifulSoup(driver.page_source, 'lxml')
            pret_element = soup.find(attrs={'aria-label': 'price'})

        # STORIA
        elif platforma == "Storia":
            try:
                WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-cy="adPageHeaderPrice"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="redirectedFromInactiveAd"]'))
                    )
                )
            except:
                pass

            soup = BeautifulSoup(driver.page_source, 'lxml')

            if soup.find(attrs={'data-cy': 'redirectedFromInactiveAd'}):
                print(f"[Inactiv - Storia] Banner inactiv detectat: {url}")
                return None

            pret_element = soup.find('strong', {'data-cy': 'adPageHeaderPrice'})

        # READ THE PRICE
        if pret_element:
            pret = clean_price(pret_element.get_text(strip=True))
            if pret:
                return pret

        print(f"[Activ - pret neidentificat] {url}")
        return 0

    except Exception as e:
        print(f"[Eroare] {platforma} | {url} | {e}")
        return None
