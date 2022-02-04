from sqlalchemy import and_, Column, exists, Float, Integer, String, ForeignKey, MetaData, Table, DateTime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from sqlalchemy.exc import NoResultFound

metadata_obj = MetaData()

# product = Table(
#     'product', metadata_obj,
#     Column('id', Integer, primary_key=True),
#     Column('name', String, nullable=False),
#     Column('price', Float, nullable=False),
#     Column('price_per_quantity', Float, nullable=False),
#     Column('base_quantity', String),
#     Column('image_link', String),
#     Column('created_timestamp', DATETIME)
# )



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

    # def has_entry_with_same_price(self, product: 'Product', session: Session) -> bool:
    #     return self.price == product.price

