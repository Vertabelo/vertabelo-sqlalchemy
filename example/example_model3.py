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
    id = Column('id', Integer, primary_key = True)
    # Unknown SQL type: 'character(12)' 
    order_no = Column('order_no', String)
    client_id = Column('client_id', Integer, ForeignKey('client.id'))

    client = relationship('Client', foreign_keys=client_id)

class Product (Base):
    __tablename__ = "product"
    id = Column('id', Integer, primary_key = True)
    product_category_id = Column('product_category_id', Integer, ForeignKey('product_category.id'))
    # Unknown SQL type: 'character(10)' 
    sku = Column('sku', String)
    name = Column('name', Unicode)
    price = Column('price', BigInteger)
    description = Column('description', Unicode)
    image = deferred(Column('image', LargeBinary))

    product_category = relationship('ProductCategory', foreign_keys=product_category_id)

class OrderItem (Base):
    __tablename__ = "order_item"
    id = Column('id', Integer, primary_key = True)
    order_id = Column('order_id', Integer, ForeignKey('order.id'))
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    amount = Column('amount', Integer)

    order = relationship('Order', foreign_keys=order_id)
    product = relationship('Product', foreign_keys=product_id)

class ProductCategory (Base):
    __tablename__ = "product_category"
    id = Column('id', Integer, primary_key = True)
    name = Column('name', Unicode)
    parent_category_id = Column('parent_category_id', Integer, ForeignKey('product_category.id'))

    product_category = relationship('ProductCategory', foreign_keys=parent_category_id)

class Client (Base):
    __tablename__ = "client"
    id = Column('id', Integer, primary_key = True)
    full_name = Column('full_name', Unicode)
    email = Column('email', Unicode)

# end
