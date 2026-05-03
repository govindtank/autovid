"""
Database Initialization and Migration Script
Run: python scripts/init_db.py --db_url postgresql://user:pass@localhost/dbname
"""

import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.models.database_models import Base


def init_database(db_url: str = "sqlite:///autovid.db"):
    """
    Initialize database and create all tables
    
    Args:
        db_url: SQLAlchemy connection string
            Examples:
            - PostgreSQL: postgresql://user:password@localhost:5432/dbname
            - SQLite: sqlite:///path/to/database.db
    """
    # Create engine
    print(f"Initializing database: {db_url}")
    
    try:
        # Test connection
        if db_url.startswith("postgresql"):
            from psycopg2 import OperationalError
            engine = create_engine(db_url)
            
            with engine.connect() as conn:
                # Check if tables already exist
                result = conn.execute(text("SELECT COUNT(*) FROM projects LIMIT 1"))
                if result.fetchone()[0] > 0:
                    print("✓ Database already initialized. Tables exist.")
                    return
                
        elif db_url.startswith("sqlite"):
            # For SQLite, just create the tables
            Base.metadata.create_all(bind=create_engine(db_url))
            print("✓ SQLite database created successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    if db_url.startswith("postgresql"):
        # Create tables for PostgreSQL
        engine = create_engine(db_url)
        Base.metadata.create_all(bind=engine)
        print("✓ PostgreSQL tables created successfully")


def main():
    parser = argparse.ArgumentParser(description="Initialize AutoVid database")
    parser.add_argument(
        "--db_url",
        type=str,
        default="postgresql://autovid:autovid@localhost/autovid",
        help="Database connection URL (default shown)"
    )
    
    args = parser.parse_args()
    init_database(args.db_url)


if __name__ == "__main__":
    main()
