from sqlalchemy import text
from Database.db_manager import SessionLocal

def normalize_db():
    session = SessionLocal()
    try:
        sql_commands = [
            # 1. Populează Tabelul Judete
            """
            INSERT INTO judete (nume_judet) 
            SELECT DISTINCT INITCAP(TRIM(TRANSLATE(judet, 'ăâîșțşţĂÂÎȘȚŞŢ', 'aaiststAAISTST'))) 
            FROM raw_data 
            WHERE judet IS NOT NULL AND processed = false
            ON CONFLICT (nume_judet) DO NOTHING;
            """,
            
            # 2. Populează Tabelul Localitati
            """
            INSERT INTO localitati (nume_localitate, id_judet)
            SELECT DISTINCT 
                INITCAP(TRIM(TRANSLATE(raw.oras, 'ăâîșțşţĂÂÎȘȚŞŢ', 'aaiststAAISTST'))), 
                j.id_judet 
            FROM raw_data raw
            JOIN judete j ON INITCAP(TRIM(TRANSLATE(raw.judet, 'ăâîșțşţĂÂÎȘȚŞŢ', 'aaiststAAISTST'))) = j.nume_judet
            WHERE raw.processed = false
            AND NOT EXISTS (
                SELECT 1 FROM localitati l 
                WHERE l.nume_localitate = INITCAP(TRIM(TRANSLATE(raw.oras, 'ăâîșțşţĂÂÎȘȚŞŢ', 'aaiststAAISTST'))) 
                AND l.id_judet = j.id_judet
            );  
            """,

            # 3. Populează Tabelul PerioadaAnConstructie
            """
            INSERT INTO perioada_an_constructie (perioada_constructie)
            SELECT DISTINCT perioada_constructie FROM raw_data
            WHERE perioada_constructie IS NOT NULL AND processed = false
            ON CONFLICT (perioada_constructie) DO NOTHING;
            """,
            
            # 4. COMPARTIMENTARE
            """
            INSERT INTO compartimentare (nume_compartimentare)
            SELECT DISTINCT compartimentare
            FROM raw_data
            WHERE compartimentare IS NOT NULL AND processed = false
            ON CONFLICT (nume_compartimentare) DO NOTHING;
            """,
            
            # 5. TIPURI IMOBIL (Curățare la inserare)
            """
            INSERT INTO tipuri_imobil (nume_tip)
            SELECT DISTINCT 
                CASE
                    WHEN tip_imobiliar ILIKE '%apartament%' OR tip_imobiliar ILIKE '%garsonier%' THEN 'Apartament'
                    WHEN tip_imobiliar ILIKE '%cas%' OR tip_imobiliar ILIKE '%vil%' OR tip_imobiliar ILIKE '%duplex%' THEN 'Casa'
                    WHEN tip_imobiliar ILIKE '%teren%' THEN 'Teren'
                    WHEN tip_imobiliar ILIKE '%spații%' OR tip_imobiliar ILIKE '%spati%' OR tip_imobiliar ILIKE '%birou%' THEN 'Spatii comerciale'
                    ELSE 'Altele'
                END
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
            """
            INSERT INTO anunturi (
                id_localitate, 
                id_tip_imobiliar,
                id_tip_tranzactie, 
                id_perioada_constructie,
                id_compartimentare,
                suprafata, 
                etaj, 
                an_constructie, 
                compartimentare, 
                pret, 
                URL_anunt,
                data_publicare, 
                id_sursa_raw
            )
            SELECT 
                l.id_localitate, 
                ti.id_tip_imobiliar, 
                tt.id_tip_tranzactie, 
                p.id_an_constructie,
                c.id_compartimentare,
                raw.suprafata, 
                CASE 
                    WHEN raw.etaj ILIKE 'parter' THEN '0'
                    ELSE raw.etaj
                END,
                raw.an_constructie, 
                raw.compartimentare, 
                raw.pret, 
                raw.URL_anunt,
                raw.data, 
                raw.id_raw
            FROM raw_data raw
            JOIN judete j ON INITCAP(TRIM(TRANSLATE(raw.judet, 'ăâîșțşţĂÂÎȘȚŞŢ', 'aaiststAAISTST'))) = j.nume_judet
            JOIN localitati l ON INITCAP(TRIM(TRANSLATE(raw.oras, 'ăâîșțşţĂÂÎȘȚŞŢ', 'aaiststAAISTST'))) = l.nume_localitate AND l.id_judet = j.id_judet
            LEFT JOIN tipuri_imobil ti ON 
                (CASE
                    WHEN raw.tip_imobiliar ILIKE '%apartament%' OR raw.tip_imobiliar ILIKE '%garsonier%' THEN 'Apartament'
                    WHEN raw.tip_imobiliar ILIKE '%cas%' OR raw.tip_imobiliar ILIKE '%vil%' OR raw.tip_imobiliar ILIKE '%duplex%' THEN 'Casa'
                    WHEN raw.tip_imobiliar ILIKE '%teren%' THEN 'Teren'
                    WHEN raw.tip_imobiliar ILIKE '%spații%' OR raw.tip_imobiliar ILIKE '%spati%' OR raw.tip_imobiliar ILIKE '%birou%' THEN 'Spatii comerciale'
                    ELSE 'Altele'
                END) = ti.nume_tip
                
            LEFT JOIN tipuri_tranzactie tt ON raw.tip_tranzactie = tt.nume_tranzactie
            LEFT JOIN perioada_an_constructie p ON raw.perioada_constructie = p.perioada_constructie
            LEFT JOIN compartimentare c ON raw.compartimentare = c.nume_compartimentare
            WHERE raw.processed = false
            AND NOT EXISTS (
                SELECT 1 FROM anunturi a WHERE a.id_sursa_raw = raw.id_raw
            );
            """,
            # 8. ISTORIC ANUNȚURI (Adăugarea prețului inițial)
            # Este esențial ca fiecare anunț nou creat să primească o primă înregistrare cu prețul de start.
            """
            INSERT INTO istoric_anunturi (id_anunt, pret, status_anunt, data_inceput)
            SELECT a.id_anunt, a.pret, 'activ', a.data_publicare
            FROM anunturi a
            JOIN raw_data raw ON a.id_sursa_raw = raw.id_raw
            WHERE raw.processed = false
            AND NOT EXISTS (
                SELECT 1 FROM istoric_anunturi ia WHERE ia.id_anunt = a.id_anunt
            );
            """,

            # 9. Marcare Date ca Procesate
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