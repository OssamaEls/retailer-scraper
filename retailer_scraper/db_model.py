from sqlalchemy import Column, Float, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import NoResultFound


Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    price_per_quantity = Column(Float)
    base_quantity = Column(String)
    image_link = Column(String)
    created_time = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def get_entry_if_exists(cls, product: 'Product', session: Session) -> bool:
        try:
            return session.query(
                Product
            ).filter(
                    Product.id == product.id
            ).one()
        except NoResultFound:
            return None


