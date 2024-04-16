import logging
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL database connection details
user = 'user'
password = 'password'
host = 'postgres'
port = '5432'
databaseName = 'stock_exchange'

SQLALCHEMY_DATABASE_URL = f'postgresql://{user}:{password}@{host}:{port}/{databaseName}'

# Create a SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
