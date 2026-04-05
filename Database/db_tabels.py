from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, func, BigInteger
from sqlalchemy.orm import relationship
from Database.db_manager import Base

class Estate(Base):
    __tablename__ = "raw_data"
    
    id_raw = Column(String(900), primary_key=True) 
    URL_anunt = Column(String(500), nullable=True)
    judet = Column(String(255), nullable=False)
    oras = Column(String(255), nullable=False)
    suprafata = Column(Integer, nullable=True)
    etaj = Column(String(255), nullable=True) 
    perioada_constructie = Column(String(255), nullable=True)
    an_constructie = Column(String(255), nullable=True)
    compartimentare = Column(String(255), nullable=True)
    camere = Column(String(255), nullable=True) 
    pret = Column(BigInteger, nullable=False)  # ← CHANGED: BigInteger supports up to 9,223,372,036,854,775,807
    tip_tranzactie = Column(String(50), nullable=True)
    tip_imobiliar = Column(String(50), nullable=True)
    platforma = Column(String(50), nullable=True)
    data = Column(Date, nullable=False)
    processed = Column(Boolean, nullable=False, default=False)
    
class Judet(Base):
    __tablename__ = 'judete'

    id_judet = Column(Integer, primary_key=True, autoincrement=True)
    nume_judet = Column(String(255), unique=True, nullable=False)
    localitati = relationship("Localitate", back_populates="judet", cascade="all, delete-orphan")
    
class Localitate(Base):
    __tablename__ = 'localitati'

    id_localitate = Column(Integer, primary_key=True, autoincrement=True)
    id_judet = Column(Integer, ForeignKey('judete.id_judet'), nullable=False)
    nume_localitate = Column(String(255), nullable=False)

    judet = relationship("Judet", back_populates="localitati")
    anunturi = relationship("Anunt", back_populates="localitate")

class TipImobil(Base):
    __tablename__ = 'tipuri_imobil'

    id_tip_imobiliar = Column(Integer, primary_key=True, autoincrement=True)
    nume_tip = Column(String(50), unique=True, nullable=False)
    anunturi = relationship("Anunt", back_populates="tip_imobiliar")

class TipTranzactie(Base):
    __tablename__ = 'tipuri_tranzactie'

    id_tip_tranzactie = Column(Integer, primary_key=True, autoincrement=True)
    nume_tranzactie = Column(String(50), unique=True, nullable=False)
    anunturi = relationship("Anunt", back_populates="tip_tranzactie")
    
class PerioadaAnConstructie(Base):
    __tablename__ = 'perioada_an_constructie'

    id_an_constructie = Column(Integer, primary_key=True, autoincrement=True)
    perioada_constructie = Column(String(255), unique=True, nullable=False)
    anunturi = relationship("Anunt", back_populates="perioada_ref")
    
class Compartimentare(Base):
    __tablename__ = 'compartimentare'

    id_compartimentare = Column(Integer, primary_key=True, autoincrement=True)
    nume_compartimentare = Column(String(255), unique=True, nullable=False)
    anunturi = relationship("Anunt", back_populates="compartimentare_ref")
    
class Anunt(Base):
    __tablename__ = 'anunturi'

    id_anunt = Column(Integer, primary_key=True, autoincrement=True)
    
    # Chei Externe
    id_localitate = Column(Integer, ForeignKey('localitati.id_localitate'), nullable=False)
    id_tip_imobiliar = Column(Integer, ForeignKey('tipuri_imobil.id_tip_imobiliar'))
    id_tip_tranzactie = Column(Integer, ForeignKey('tipuri_tranzactie.id_tip_tranzactie'))
    id_perioada_constructie = Column(Integer, ForeignKey('perioada_an_constructie.id_an_constructie'))
    id_compartimentare = Column(Integer, ForeignKey('compartimentare.id_compartimentare'))
    
    # Atribute
    suprafata = Column(Integer)
    etaj = Column(String(255))
    an_constructie = Column(String(255)) # Valoarea brută (ex: "2020")
    compartimentare = Column(String(255))
    pret = Column(BigInteger, nullable=False)
    URL_anunt = Column(String(500), nullable=True)
    data_publicare = Column(Date)
    id_sursa_raw = Column(String(255), ForeignKey('raw_data.id_raw'))

    # Relații (Dependențele)
    localitate = relationship("Localitate", back_populates="anunturi")
    tip_imobiliar = relationship("TipImobil", back_populates="anunturi")
    tip_tranzactie = relationship("TipTranzactie", back_populates="anunturi")
    perioada_ref = relationship("PerioadaAnConstructie", back_populates="anunturi")
    compartimentare_ref = relationship("Compartimentare", back_populates="anunturi")
    istoric_anunturi = relationship("IstoricAnunt", back_populates="anunt_legatura", cascade="all, delete-orphan")
    sursa_raw = relationship("Estate")
class IstoricAnunt(Base):
    __tablename__ = 'istoric_anunturi'
    id_istoric = Column(Integer, primary_key=True, autoincrement=True)
    id_anunt = Column(Integer, ForeignKey('anunturi.id_anunt'), nullable=False)
    
    pret = Column(BigInteger, nullable=False)  # ← CHANGED: Integer → BigInteger
    status_anunt = Column(String(50), nullable=False, default="activ")
    data_inceput = Column(Date, nullable=False)
    data_sfarsit = Column(Date, nullable=True)

    # RELAȚIA BACK
    anunt_legatura = relationship("Anunt", back_populates="istoric_anunturi")