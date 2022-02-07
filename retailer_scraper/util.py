from typing import Dict, Optional
import os
from pathlib import Path

import json
import requests

from bs4 import BeautifulSoup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from db_model import Base
from headers import headers


def parse_html(url: str) -> BeautifulSoup:
    """
    Get a BeautifulSoup object from an url.
    Parameters
    ----------
    url
    Returns
    -------
        BeautifulSoup object wrapping the html content of the web page
    """
    output = requests.get(url, headers=headers, timeout=10)
    page = output.text
    return BeautifulSoup(page, 'html.parser')


def get_text(
        bs: BeautifulSoup,
        *,
        name: str,
        attrs: Optional[Dict]
) -> str:
    """
    Parameters
    ----------
    bs : BeautifulSoup
        Object wrapping some html content
    name
    attrs
        Parameters to bs
    Returns
    -------
    str
        Text wrapped by the soup request or a default string if soup is None
    """
    soup = bs.find(name=name, attrs=attrs)
    return soup.text if soup is not None else "Info not available"


def to_json(details: Dict, item_directory: Path):
    os.makedirs(item_directory, exist_ok=True)
    with open(item_directory / 'data.json', 'w', encoding='utf8') as f:
        json.dump(details, f, indent=4, ensure_ascii=False)


def make_session() -> Session:
    """
    Create an SQLAlchemy session to interact with the database
    Returns
    -------
    An SQLAlchemy Session
    """
    db_name = os.environ['db_name']
    username = os.environ['username']
    password = os.environ['password']
    host = os.environ['host']
    port = 5432

    database_url = f'postgresql://{username}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(database_url, poolclass=NullPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session

