import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from retailer_scraper.db_model import Base, Product


@pytest.fixture(name='session')
def make_session():
    engine = create_engine('sqlite://')
    session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    yield session
    session.rollback()
    engine.dispose()


@pytest.fixture
def product1():
    return Product(
        id=1,
        name='product1',
        category='category1',
        price=10,
        price_per_quantity=1,
        base_quantity='100g',
        image_link='www.example.com'
    )


@pytest.fixture
def product2():
    return Product(
        id=2,
        name='product',
        category='category1',
        price=10,
        price_per_quantity=1,
        base_quantity='100g',
        image_link='www.example.com'
    )


@pytest.fixture
def product3():
    return Product(
        id=1,
        name='product',
        category='category1',
        price=9,
        price_per_quantity=0.9,
        base_quantity='100g',
        image_link='www.example.com'
    )


@pytest.fixture(autouse=True)
def add_product(product1, session):
    session.add(product1)


def test_has_no_entry(product2, session):
    assert Product.get_entry_if_exists(product2, session) is None


def test_has_entry(product3, session, product1):
    assert Product.get_entry_if_exists(product3, session) == product1
