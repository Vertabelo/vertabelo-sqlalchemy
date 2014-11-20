#! /usr/bin/python -i

# -*- coding: utf-8 -*-

# Copyright 2014 Vertabelo.com <contact@vertabelo.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

engine = create_engine('sqlite:///example.db', echo=False)

Session = sessionmaker(bind=engine)
Session = sessionmaker()
Session.configure(bind=engine) 
session = Session()

import example_model
from example_model import Product
from example_model import ProductCategory
from example_model import OrderItem


# hard coded id 
current_order_id = 1

def categories():
    for pc in session.query(ProductCategory):
        print pc.name


def products():
    print "%-5s - %-20s - %s" % ("SKU", "NAME", "PRICE")
    print "-" * 36
    for p in session.query(Product):
        print "%-5s - %-20s - $%s" % (p.sku, p.name, p.price)



def get_product_by_sku(sku):

    try: 
        return session.query(Product).filter(Product.sku == sku).one()
    except NoResultFound, e:
        return None


def add(sku, amount):

    p = get_product_by_sku(sku)

    if(p == None):
        print "No such product '%s'" % (sku)
        return

    order_item = None

    try:
        order_item =  session.query(OrderItem).filter(OrderItem.product_id == p.id, OrderItem.order_id == current_order_id).one()
    except NoResultFound, e:
        order_item = OrderItem()
        order_item.id = p.id # FIXME this should be taken from a sequence
        order_item.product_id = p.id
        order_item.order_id = current_order_id
        order_item.amount = 0 

    order_item.amount += amount
    session.add(order_item)
    session.commit()

def show():

    for order_item in session.query(OrderItem).filter(OrderItem.order_id == current_order_id):
        print "%-5s - %-20s - %-5s - $%s" % (order_item.product.sku, order_item.product.name, order_item.amount, order_item.product.price)


print "Welcome to the Sample Shop !!!"
print
print "commands:"
print "products()         - displays what we've got on a shelf" 
print "add(sku, amount)   - adds product to your order"
print "show()             - shows your order"

