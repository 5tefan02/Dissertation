import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from Database.db_manager import SessionLocal
from Database.db_tabels import Estate, Anunt, IstoricAnunt

from Data.verificare_status import verificare_status

def verifica_si_actualizeaza_preturi():
    session = SessionLocal()
    
    # Selectăm anunțurile curente cu URL valid
    anunturi_de_verificat = session.query(Anunt, Estate).join(
        Estate, Anunt.id_sursa_raw == Estate.id_raw
    ).filter(Estate.URL_anunt.isnot(None)).all()
    
    if not anunturi_de_verificat:
        print("Nu s-au găsit anunțuri cu URL valid în baza de date.")
        session.close()
        return

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    print("Pornire driver Selenium...")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    
    azi = date.today()
    schimbari = 0
    inactivate = 0

    try:
        for anunt, raw_data in anunturi_de_verificat:
            url = raw_data.URL_anunt
            platforma = raw_data.platforma
            pret_vechi = anunt.pret
            
            print(f"Se verifică: {url}")
            
            # Apelăm funcția izolată în fișierul price_scraper.py
            pret_nou = verificare_status(driver, url, platforma)
            
            istoric_activ = session.query(IstoricAnunt).filter(
                IstoricAnunt.id_anunt == anunt.id_anunt,
                IstoricAnunt.status_anunt == 'activ'
            ).first()
            
            # 1. Anunț Inactiv
            if pret_nou is None:
                if istoric_activ:
                    istoric_activ.status_anunt = 'inactiv'
                    istoric_activ.data_sfarsit = azi
                    inactivate += 1
                    print(" -> Anunț devenit INACTIV.")
                continue

            # 2. Preț neidentificat (Anunț activ dar fără preț)
            if pret_nou == 0:
                print(f" -> Anunț ACTIV (preț neidentificat). Nicio schimbare.")
                if not istoric_activ:
                    istoric_nou = IstoricAnunt(
                        id_anunt=anunt.id_anunt,
                        pret=pret_vechi,
                        status_anunt='activ',
                        data_inceput=azi
                    )
                    session.add(istoric_nou)
                continue

            # 3. Preț Schimbat
            if pret_nou != pret_vechi:
                print(f" -> PREȚ SCHIMBAT! Vechi: {pret_vechi} | Nou: {pret_nou}")
                
                anunt.pret = pret_nou
                
                if istoric_activ:
                    istoric_activ.data_sfarsit = azi
                    istoric_activ.status_anunt = 'modificat'
                
                istoric_nou = IstoricAnunt(
                    id_anunt=anunt.id_anunt,
                    pret=pret_nou,
                    status_anunt='activ',
                    data_inceput=azi,
                    data_sfarsit=None
                )
                session.add(istoric_nou)
                schimbari += 1
                
            # 4. Preț Neschimbat (Reparare istoric lipsă, dacă e cazul)
            elif not istoric_activ:
                istoric_nou = IstoricAnunt(
                    id_anunt=anunt.id_anunt,
                    pret=pret_vechi,
                    status_anunt='activ',
                    data_inceput=azi
                )
                session.add(istoric_nou)
            
            # 5. Anunț activ dar fără preț (don't update price logic)
            else:
                print(f" -> Anunț ACTIV (preț neidentificat). Nicio schimbare.")

        # Salvăm toate modificările în baza de date
        session.commit()
        print(f"\nFinalizat! S-au modificat {schimbari} prețuri și s-au inactivat {inactivate} anunțuri.")

    except Exception as e:
        session.rollback()
        print(f"Eroare critică pe parcursul procesării: {e}")
    finally:
        driver.quit()
        session.close()

