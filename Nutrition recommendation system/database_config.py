"""
Database Configuration for Nutrition Recommendation System
Supports both PostgreSQL and SQLite databases
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# PostgreSQL specific configuration
POSTGRES_CONFIG = {
    'host': config('POSTGRES_HOST', default='localhost'),
    'port': config('POSTGRES_PORT', default=5432, cast=int),
    'database': config('POSTGRES_DB', default='nutrition_db'),
    'user': config('POSTGRES_USER', default='postgres'),
    'password': config('POSTGRES_PASSWORD', default='password')
}

def get_postgres_url():
    """Generate PostgreSQL connection URL"""
    return f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"

# SQLite specific configuration
SQLITE_CONFIG = {
    'database_path': config('SQLITE_DB_PATH', default='nutrition_system.db')
}

def get_sqlite_url():
    """Generate SQLite connection URL"""
    return f"sqlite:///{SQLITE_CONFIG['database_path']}"

# Database Configuration with dynamic URL generation
def get_database_url():
    """Generate database URL based on environment configuration"""
    db_type = config('DB_TYPE', default='sqlite').lower()
    
    if db_type == 'postgresql':
        return get_postgres_url()
    else:
        return get_sqlite_url()

DATABASE_URL = get_database_url()

# Create engine with proper configuration
engine = create_engine(
    DATABASE_URL,
    echo=config('DEBUG', default=False, cast=bool),
    # SQLite specific settings
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

def reset_db():
    """Reset database (drop and recreate all tables)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset successfully!")

# Database connection test
def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1"))
            print(f"Database connection successful: {result.fetchone()}")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
