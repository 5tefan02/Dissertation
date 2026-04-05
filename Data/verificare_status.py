from bs4 import BeautifulSoup
import time
import re

def verificare_status(driver, url, platforma):
    """
    Accesează URL-ul folosind driver-ul Selenium curent și extrage prețul.
    Returnează prețul (int) sau None dacă anunțul este inactiv/șters.
    """
    try:
        driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        # --- 1. VERIFICARE EXPLICITĂ PENTRU ANUNȚ INACTIV ---
        text_pagina = soup.get_text().lower()
        if "acest anunț nu mai este valabil" in text_pagina or "anunț dezactivat" in text_pagina or "nu a fost gasita" in text_pagina:
            print(f" [Confirmat Inactiv] Anunțul a fost dezactivat de utilizator: {url}")
            return None

        # --- 2. EXTRAGERE PREȚ PENTRU FIECARE PLATFORMĂ ---
        pret_element = None
        
        if platforma == "OLX":
            pret_element = soup.find(attrs={"data-testid": "ad-price"})
            if not pret_element:
                pret_element = soup.find(['h3', 'div'], class_=re.compile(r'css-1j840l6|css-90xrc0'))
            if not pret_element:
                pret_element = soup.find('h3', class_=re.compile(r'css-'))
                
        elif platforma == "imobiliare.ro":
            pret_element = soup.find('div', {'aria-label': 'price'})
            if not pret_element:
                pret_element = soup.find('span', {'aria-label': 'price'})
            if not pret_element:
                pret_element = soup.find(['div', 'span'], class_=re.compile(r'price'))
                
        elif platforma == "Storia":
            pret_element = soup.find('strong', {'data-cy': 'adPageHeaderPrice'})
            if not pret_element:
                pret_element = soup.find(['strong', 'span'], class_=re.compile(r'price'))
        
        if pret_element:
            return int(''.join(c for c in pret_element.text if c.isdigit()))
        
        # --- 3. VERIFICARE FINALĂ: ACTIVE vs INACTIVE ---
        # Dacă URL-ul se încarcă cu succes și NU conține text de inactiv, e activ
        if not any(text in text_pagina for text in ["error", "404", "not found", "defunct", "removed"]):
            print(f"✓ [Activ - Preț neidentificat] URL funcțional: {url}")
            return 0  # Returnează 0 pentru a indica "active but price not found"
        
        print(f"[Inactiv] Pagina nu se a putut procesa corect: {url}")
        return None
            
    except Exception as e:
        print(f"Eroare la extragerea prețului pentru {url} ({platforma}): {e}")
        return None