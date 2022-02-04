from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from retailer_scraper.db_config import config
from retailer_scraper.db_model import Base


def make_session():
    db_name = config['db_name']
    username = config['username']
    password = config['password']
    host = config['host']
    port = config['port']

    database_url = f'postgresql://{username}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(database_url, poolclass=NullPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session

