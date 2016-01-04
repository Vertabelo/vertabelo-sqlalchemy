# -*- encoding: utf-8 -*-
# begin

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger,String, ForeignKey, Unicode, Binary, LargeBinary, Time, DateTime, Date, Text, Boolean, Float
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.orm import sessionmaker

Base = declarative_base()



class Order (Base):
    __tablename__ = "order"
    # describe me please
    id = Column('id', Integer, primary_key = True)
    # describe me pleaseUnknown SQL type: 'character(12)' 
    order_no = Column('order_no', String)
    # describe me please
    client_id = Column('client_id', Integer, ForeignKey('client.id'))

    client = relationship('Client', foreign_keys=client_id)

class Product (Base):
    __tablename__ = "product"
    # describe me please
    id = Column('id', Integer, primary_key = True)
    # describe me please
    product_category_id = Column('product_category_id', Integer, ForeignKey('product_category.id'))
    # describe me pleaseUnknown SQL type: 'character(10)' 
    sku = Column('sku', String)
    # describe me please
    name = Column('name', Unicode)
    # describe me please
    price = Column('price', BigInteger)
    # describe me please
    description = Column('description', Unicode)
    # describe me please
    image = deferred(Column('image', LargeBinary))

    product_category = relationship('ProductCategory', foreign_keys=product_category_id)

class OrderItem (Base):
    __tablename__ = "order_item"
    # describe me please
    id = Column('id', Integer, primary_key = True)
    # describe me please
    order_id = Column('order_id', Integer, ForeignKey('order.id'))
    # describe me please
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    # describe me please
    amount = Column('amount', Integer)

    order = relationship('Order', foreign_keys=order_id)
    product = relationship('Product', foreign_keys=product_id)

class ProductCategory (Base):
    __tablename__ = "product_category"
    # describe me please
    id = Column('id', Integer, primary_key = True)
    # describe me please
    name = Column('name', Unicode)
    # describe me please
    parent_category_id = Column('parent_category_id', Integer, ForeignKey('product_category.id'))

    product_category = relationship('ProductCategory', foreign_keys=parent_category_id)

class Client (Base):
    __tablename__ = "client"
    # describe me please
    id = Column('id', Integer, primary_key = True)
    # describe me please
    full_name = Column('full_name', Unicode)
    # describe me please
    email = Column('email', Unicode)

# end
