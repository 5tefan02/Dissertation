from Database.db_tabels import Estate
from Database.db_manager import SessionLocal
from sqlalchemy import text

def insert_estates(rezultate: list[dict]):
    if not rezultate:
        return

    session = SessionLocal()

    # --- 1. FILTRAREA DATELOR (Scutul de protecție) ---
    rezultate_curate = []
    
    for anunt in rezultate:
        # Verificăm ca datele obligatorii (NOT NULL în DB) să existe și să nu fie "N/A"
        if (anunt.get('judet') and anunt.get('judet') != "N/A" and 
            anunt.get('oras') and anunt.get('oras') != "N/A" and 
            anunt.get('pret') is not None and 
            anunt.get('id_raw')):
            
            rezultate_curate.append(anunt)
        else:
            print(f"[DB-Skip] Ignorat anunț invalid/fără locație: {anunt.get('URL_anunt')}")

    # Dacă după filtrare nu a mai rămas nimic valid, oprim execuția să nu dăm eroare de SQL gol
    if not rezultate_curate:
        print("[DB] Niciun anunț valid pentru inserare în acest lot.")
        session.close()
        return

    # --- 2. INSERAREA EFECTIVĂ (Doar cu date perfecte) ---
    query = text("""INSERT INTO raw_data (
            id_raw, "URL_anunt", judet, oras, suprafata, etaj, 
            perioada_constructie, an_constructie, compartimentare, 
            camere, tip_tranzactie, tip_imobiliar, platforma, pret, data, processed
        ) VALUES (
            :id_raw, :URL_anunt, :judet, :oras, :suprafata, :etaj, 
            :perioada_constructie, :an_constructie, :compartimentare, 
            :camere, :tip_tranzactie, :tip_imobiliar, :platforma, :pret, :data, :processed
        )
        ON CONFLICT (id_raw) DO NOTHING;
    """)
    
    try:
        # Executăm toată lista CURATĂ odată (foarte rapid)
        session.execute(query, rezultate_curate)
        session.commit()
        print(f"[DB] Procesare finalizată. {len(rezultate_curate)} date noi (valide) au fost inserate, duplicatele au fost ignorate.")
    except Exception as e:
        session.rollback()
        print(f"[DB] Eroare: {e}")
    finally:
        session.close()