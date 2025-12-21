from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL


Base = declarative_base()

class Estate(Base):
    __tablename__ = "real_estate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    judet = Column(String, nullable=True)
    oras = Column(String, nullable=True)
    suprafata = Column(Integer, nullable=True)
    etaj = Column(String, nullable=True)
    an_constructie = Column(String, nullable=True)
    compartimentare = Column(String, nullable=True)
    pret = Column(Integer, nullable=False)


DB_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="1234",      # 🔴 schimbă parola
    host="localhost",
    port=5432,
    database="Scooby"     # 🔴 schimbă DB dacă e nevoie
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
                judet=r["judet"],
                oras=r["oras"],
                suprafata=r["suprafata"],
                etaj=r["etaj"],
                an_constructie=r["an_constructie"],
                compartimentare=r.get("compartimentare"),
                pret=r["pret"],
            )
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