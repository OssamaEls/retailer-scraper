from sqlalchemy import Column, Float, Integer, String, DATETIME, ForeignKey, MetaData,Table

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

metadata_obj = MetaData()

product = Table(
    'product', metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('price', Float, nullable=False),
    Column('price_per_quantity', Float, nullable=False),
    Column('base_quantity', String),
    Column('image_link', String)
)



# Base = declarative_base()
#
#
# class Product(Base):
#     __tablename__ = 'product'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     price = Column(Float, nullable=False)
#     price_per_quantity = Column(Float)
#     base_quantity = Column(String)
#     image_link = Column(String)

