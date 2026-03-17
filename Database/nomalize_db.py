from sqlalchemy import text
from Database.db_manager import SessionLocal

def normalize_db():
    session = SessionLocal()
    try:
        sql_commands = [
            # 1. Populează Tabelul Judete
            """
            INSERT INTO judete (nume_judet) 
            SELECT DISTINCT judet FROM raw_data 
            WHERE judet IS NOT NULL AND processed = false
            ON CONFLICT (nume_judet) DO NOTHING;
            """,
            
            # 2. Populează Tabelul Localitati
            # Folosim JOIN cu judete pentru a asigura legătura corectă
            """
            INSERT INTO localitati (nume_localitate, id_judet)
            SELECT DISTINCT raw.oras, j.id_judet 
            FROM raw_data raw
            JOIN judete j ON raw.judet = j.nume_judet
            WHERE raw.processed = false
            AND NOT EXISTS (
                SELECT 1 FROM localitati l 
                WHERE l.nume_localitate = raw.oras AND l.id_judet = j.id_judet
            );  
            """,

            # 3. Populează Tabelul PerioadaAnConstructie
            """
            INSERT INTO perioada_an_constructie (perioada_constructie)
            SELECT DISTINCT perioada_constructie FROM raw_data
            WHERE perioada_constructie IS NOT NULL AND processed = false
            ON CONFLICT (perioada_constructie) DO NOTHING;
            """,
            
            # 4. COMPARTIMENTARI
            """
            INSERT INTO compartimentari (nume_compartimentare)
            SELECT DISTINCT compartimentare
            FROM raw_data
            WHERE compartimentare IS NOT NULL AND processed = false
            ON CONFLICT (nume_compartimentare) DO NOTHING;
            """,
            
            # 5. TIPURI IMOBIL
            """
            INSERT INTO tipuri_imobil (nume_tip)
            SELECT DISTINCT tip_imobiliar
            FROM raw_data
            WHERE tip_imobiliar IS NOT NULL AND processed = false
            ON CONFLICT (nume_tip) DO NOTHING;
            """,
            
              # 6. TIPURI TRANZACTIE
            """
            INSERT INTO tipuri_tranzactie (nume_tranzactie)
            SELECT DISTINCT tip_tranzactie
            FROM raw_data
            WHERE tip_tranzactie IS NOT NULL AND processed = false
            ON CONFLICT (nume_tranzactie) DO NOTHING;
            """,

            # 7. Inserarea Finală în Tabelul Anunturi
            # Corelăm toate ID-urile din tabelele de nomenclator
            """
            INSERT INTO anunturi (
                id_localitate, 
                id_tip_imobiliar,
                id_tip_tranzactie, 
                id_perioada_constructie,
                suprafata, 
                etaj, an_constructie, 
                compartimentare, 
                pret, 
                ata_publicare, 
                id_sursa_raw
            )
            SELECT 
                l.id_localitate, 
                ti.id_tip_imobiliar, 
                tt.id_tip_tranzactie, 
                p.id_an_constructie,
                raw.suprafata, 
                raw.etaj, 
                raw.an_constructie, 
                raw.compartimentare, 
                raw.pret, 
                raw.data, 
                raw.id_raw
            FROM raw_data raw
            JOIN judete j ON raw.judet = j.nume_judet
            JOIN localitati l ON raw.oras = l.nume_localitate AND l.id_judet = j.id_judet
            LEFT JOIN tipuri_imobil ti ON raw.tip_imobiliar = ti.nume_tip
            LEFT JOIN tipuri_tranzactie tt ON raw.tip_tranzactie = tt.nume_tranzactie
            LEFT JOIN perioada_an_constructie p ON raw.perioada_constructie = p.perioada_constructie
            LEFT JOIN compartimentari c ON raw.compartimentare = c.nume_compartimentare
            WHERE raw.processed = false;
            """,

            # 5. Marcare Date ca Procesate
            """
            UPDATE raw_data 
            SET processed = true 
            WHERE processed = false
            AND id_raw IN (
                SELECT id_sursa_raw FROM anunturi);
            """
        ]

        print("--- Start Proces Normalizare ---")
        
        for i, command in enumerate(sql_commands, 1):
            result = session.execute(text(command))
            print(f"Pasul {i} executat. Rânduri afectate: {result.rowcount}")
        
        session.commit()
        print("--- Succes: Datele au fost normalizate cu succes! ---")

    except Exception as e:
        session.rollback()
        print(f"!!! Eroare critică la normalizare: {e}")
    finally:
        session.close()