from Database.db_tabels import Estate
from Database.db_manager import SessionLocal
from sqlalchemy import text


def insert_estates(rezultate: list[dict]):
    session = SessionLocal()

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
        # Executăm toată lista odată (foarte rapid)
        session.execute(query, rezultate)
        session.commit()
        print(f"[DB] Procesare finalizată. Datele noi au fost inserate, duplicatele au fost ignorate.")
    except Exception as e:
        session.rollback()
        print(f"[DB] Eroare: {e}")
    finally:
        session.close()