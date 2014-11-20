-- Created by Vertabelo (http://vertabelo.com)
-- Script type: create
-- Scope: [tables, references, sequences, views, procedures]
-- Generated at Thu Nov 20 10:07:00 UTC 2014



-- tables
-- Table: client
CREATE TABLE client (
    id integer NOT NULL  PRIMARY KEY,
    full_name varchar(255) NOT NULL,
    email varchar(255) NOT NULL
);

-- Table: "order"
CREATE TABLE "order" (
    id integer NOT NULL  PRIMARY KEY,
    order_no character(12) NOT NULL,
    client_id integer NOT NULL,
    FOREIGN KEY (client_id) REFERENCES client (id)
);

-- Table: order_item
CREATE TABLE order_item (
    id integer NOT NULL  PRIMARY KEY,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    amount integer NOT NULL,
    FOREIGN KEY (order_id) REFERENCES "order" (id),
    FOREIGN KEY (product_id) REFERENCES product (id)
);

-- Table: product
CREATE TABLE product (
    id integer NOT NULL  PRIMARY KEY,
    product_category_id integer NOT NULL,
    sku character(10) NOT NULL,
    name varchar(255) NOT NULL,
    price decimal(12,2) NOT NULL,
    description varchar(1000) NOT NULL,
    image blob NOT NULL,
    FOREIGN KEY (product_category_id) REFERENCES product_category (id)
);

-- Table: product_category
CREATE TABLE product_category (
    id integer NOT NULL  PRIMARY KEY,
    name varchar(255) NOT NULL,
    parent_category_id integer,
    FOREIGN KEY (parent_category_id) REFERENCES product_category (id)
);





-- End of file.

