from sqlalchemy import Column, Integer, String, create_engine, DateTime, Date, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL


Base = declarative_base()

class Estate(Base):
    __tablename__ = "raw_data"

    id_raw = Column(String, primary_key=True)
    judet = Column(String, nullable=False)
    oras = Column(String, nullable=False)
    suprafata = Column(Integer, nullable=True)
    etaj = Column(String, nullable=True)
    an_constructie = Column(String, nullable=True)
    compartimentare = Column(String, nullable=True)
    pret = Column(Integer, nullable=False)
    tip_tranzactie = Column(String, nullable=True)
    tip_imobiliar = Column(String, nullable=True)
    data = Column(Date, nullable=False)
    processed = Column(Boolean, nullable=False)


DB_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="1234",      # 🔴 schimbă parola
    host="localhost",
    port=5432,
    database="DB1"     # 🔴 schimbă DB dacă e nevoie
)

engine = create_engine(DB_URL, echo=False, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

Base.metadata.create_all(engine)


def insert_estates(rezultate: list[dict]):
    session = SessionLocal()

    try:
        objects = [
            Estate(
                id_raw=r["id_raw"],
                judet=r["judet"],
                oras=r["oras"],
                suprafata=r["suprafata"],
                etaj=r["etaj"],
                an_constructie=r["an_constructie"],
                compartimentare=r.get("compartimentare"),
                tip_tranzactie=r["tip_tranzactie"],
                tip_imobiliar=r["tip_imobiliar"],
                pret=r["pret"],
                data=r["data"],
                processed=r["processed"])
            for r in rezultate
        ]

        session.add_all(objects)
        session.commit()
        print(f"[DB] Inserate {len(objects)} inregistrari")

    except Exception as e:
        session.rollback()
        print("[DB] Eroare la insert:", e)
        raise

    finally:
        session.close()
        