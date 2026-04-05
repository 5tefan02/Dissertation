from Data.actualizare_status import verifica_si_actualizeaza_preturi
from Database.nomalize_db import normalize_db
from Scraping.scraper_OLX import scrape_olx
from Scraping.scraper_imobiliarero import scrape_imobiliarero
from Scraping.scraper_storia import scrape_storia
from Database.insert_estates import insert_estates
from Database.db_manager import engine, Base
import Database.db_tabels as db_tabels

def main():
    Base.metadata.create_all(bind=engine)
    
    rezultate_olx = scrape_olx()
    rezultate_imobiliarero_vanzare = scrape_imobiliarero('https://www.imobiliare.ro/vanzare-imobiliare?sort=latest', 'vanzare')
    rezultate_imobiliarero_inchiriere = scrape_imobiliarero('https://www.imobiliare.ro/inchirieri-imobiliare?sort=latest', 'inchiriere')

    if rezultate_olx:
        insert_estates(rezultate_olx)
        print(f"{len(rezultate_olx)} rezultate inserate in baza de date.")
    else:
        print("Niciun rezultat de inserat")

    if rezultate_imobiliarero_vanzare:
        insert_estates(rezultate_imobiliarero_vanzare)
        print(f"{len(rezultate_imobiliarero_vanzare)} rezultate de vanzare inserate in baza de date.")

    if rezultate_imobiliarero_inchiriere:
        insert_estates(rezultate_imobiliarero_inchiriere)
        print(f"{len(rezultate_imobiliarero_inchiriere)} rezultate de inchiriere inserate in baza de date.")
    
    rezultate_storia_vanzare_apartamente = scrape_storia('https://www.storia.ro/ro/rezultate/vanzare/apartament/toata-romania?by=LATEST&direction=DESC&limit=72', 'vanzare', 'Apartament')
    rezultate_storia_inchiriere_apartamente = scrape_storia('https://www.storia.ro/ro/rezultate/inchiriere/apartament/toata-romania?by=LATEST&direction=DESC&limit=72', 'inchiriere', 'Apartament')
    rezultate_storia_vanzare_casa = scrape_storia('https://www.storia.ro/ro/rezultate/vanzare/casa/toata-romania?by=LATEST&direction=DESC&limit=72', 'vanzare', 'Casa')
    rezultate_storia_inchiriere_casa = scrape_storia('https://www.storia.ro/ro/rezultate/inchiriere/casa/toata-romania?by=LATEST&direction=DESC&limit=72', 'inchiriere', 'Casa')
    
    if rezultate_storia_vanzare_apartamente:
        insert_estates(rezultate_storia_vanzare_apartamente)
        print(f"{len(rezultate_storia_vanzare_apartamente)} rezultate de vanzare apartamente inserate in baza de date.")
        
    if rezultate_storia_inchiriere_apartamente:
        insert_estates(rezultate_storia_inchiriere_apartamente)
        print(f"{len(rezultate_storia_inchiriere_apartamente)} rezultate de inchiriere apartamente inserate in baza de date.")
        
    if rezultate_storia_vanzare_casa:
        insert_estates(rezultate_storia_vanzare_casa)
        print(f"{len(rezultate_storia_vanzare_casa)} rezultate de vanzare case inserate in baza de date.")
    
    if rezultate_storia_inchiriere_casa:
        insert_estates(rezultate_storia_inchiriere_casa)
        print(f"{len(rezultate_storia_inchiriere_casa)} rezultate de inchiriere case inserate in baza de date.")

    normalize_db()
    verifica_si_actualizeaza_preturi()


if __name__ == "__main__":
    main() 