import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal, get_db
from app.models import Person, Car

def test_database_connection():
    """Testa se a conexão com o banco de dados SQLite em memória está funcionando"""
    assert str(engine.url) == "sqlite:///:memory:"
    
    connection = engine.connect()
    assert connection.closed is False
    
    result = connection.execute(text("SELECT 1"))
    assert result.scalar() == 1
    
    connection.close()

def test_session_creation():
    """Testa se a sessão do SQLAlchemy é criada corretamente"""
    session = SessionLocal()
    
    assert isinstance(session, Session)
    assert session.bind == engine
    assert session.autoflush is False
    
    session.close()

def test_get_db_generator():
    """Testa se o gerador get_db fornece a sessão corretamente"""
    db_gen = get_db()
    db = next(db_gen)

    assert isinstance(db, Session)
    assert db.bind == engine

def test_metadata_creation():
    """Testa se as tabelas podem ser criadas no banco de dados"""
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    assert "people" in tables
    assert "cars" in tables
    
    Base.metadata.drop_all(bind=engine)

@pytest.mark.parametrize("table,columns", [
    ("people", ["id", "name", "cpf", "birth_date"]),
    ("cars", ["id", "make", "model", "year", "color", "price", "owner_id"]),
])
def test_table_structure(table, columns):
    """Testa se as tabelas têm a estrutura correta"""
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    
    assert table in inspector.get_table_names()
    
    table_columns = [col["name"] for col in inspector.get_columns(table)]
    for column in columns:
        assert column in table_columns
    
    Base.metadata.drop_all(bind=engine)

def test_session_isolation():
    """Testa se as sessões são isoladas umas das outras"""
    session1 = SessionLocal()
    session2 = SessionLocal()
    
    assert session1 is not session2
    
    session1.close()
    session2.close()
