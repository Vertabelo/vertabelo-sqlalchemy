#! /usr/bin/python
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

import re
import sys
import getopt
from xml.dom import minidom
from xml.dom import Node


#################################################################

class CodeEmiter():

	indentLevel = 0
	indentContent = "    "
	endLineContent = "\n"

	output = u""

	def indent(self):
		self.indentLevel += 1

	def deindent(self):
		self.indentLevel -= 1

	def emit(self, content):
		self.output += (self.indentContent * self.indentLevel) + content + self.endLineContent

	def comment(self, content):

		if(content == None or content == ""):
			return

		self.emit("# " + content)

	def nl(self):
		self.output += self.endLineContent

	def vspace(self):
		self.nl()
		self.nl()
		self.nl()

	def code(self):
		return self.output.encode('utf-8')


################################################################

## Vertabelo XML as object model.

def find_subnode_by_name(node, sub_name):
	for i in node.childNodes:
		if(i.nodeName == sub_name):
			return i
	raise Exception, "couldn't find tag '%s' in '%s'" % (sub_name, node)


def subnode_value(node, sub_name):
	node = find_subnode_by_name(node,sub_name)

	if (node.firstChild == None):
		return ""

	return node.firstChild.nodeValue

class Column():

	name = None
	sql_type = None
	is_pk = False
	description = None
	is_fk = False
	table = None

	def build(self, xmlNode):
		self.id = xmlNode.attributes['Id'].value
		
		self.name =  subnode_value(xmlNode,"Name")
		self.sql_type = subnode_value(xmlNode,"Type")
		pk = subnode_value(xmlNode,"PK")

		if(pk == "true"):
			self.is_pk = True
		else:
			self.is_pk = False

		self.description = subnode_value(xmlNode, "Description")


	def column_with_table_name(self):
		return self.table.name + "." + self.name

	def __repr__(self):
		return "<Column(name='%s' type='%s' pk='%s')>"  % (self.name, self.sql_type, self.is_pk) 

	def dump(self):
		print str(self)

class Table():

	dbModel = None

	id = None
	name = None
	columns = None
	references = None

	def __init__(self):
		self.columns = []
		self.fk_references = []
		self.pk_references = []


	def findColumn(self, id):

		for i in self.columns:
			if(i.id == id):
				return i

		raise Exception, "Database model is corrupted. Couldn't find column with id: " + id

	def build(self, xmlNode):
		self.id = xmlNode.attributes['Id'].value

		self.name = subnode_value(xmlNode,"Name")
		self.description = subnode_value(xmlNode, "Description")

		columns = find_subnode_by_name(xmlNode, "Columns").childNodes

		for i in columns:
			if(i.nodeType == Node.ELEMENT_NODE):
				c = Column()
				c.build(i)
				c.table = self
				self.columns.append(c)

	
	def __repr__(self):
		return "<Table(name='%s') columns=%d>"  % (self.name, len(self.columns))

	def dump(self):
		print str(self)
		for i in self.columns:
			i.dump()


class View():
	name = None


class Reference():

	dbModel = None
	name = None

	pk_table = None
	fk_table = None

	pk_role = None
	fk_role = None

	fk_columns = None
	pk_columns = None

	def __init__(self):
		self.fk_columns = []
		self.pk_columns = []
		self.name = ""

	def build(self, xmlNode):

		self.id = xmlNode.attributes['Id'].value

		self.name = subnode_value(xmlNode, "Name")
		self.description = subnode_value(xmlNode, "Description")

		pkTableId = subnode_value(xmlNode, "PKTable")
		fkTableId = subnode_value(xmlNode, "FKTable")

		self.pk_role = subnode_value(xmlNode, "PKRole")
		self.fk_role = subnode_value(xmlNode, "FKRole")

		self.pk_table = self.dbModel.findTable(pkTableId)
		self.fk_table = self.dbModel.findTable(fkTableId)

		self.pk_table.pk_references.append(self)
		self.fk_table.fk_references.append(self)

		references = xmlNode.getElementsByTagName("ReferenceColumns")[0]

		for i in references.childNodes:
			if(i.nodeType == Node.ELEMENT_NODE):

				pkColumnId = subnode_value(i, "PKColumn")
				fkColumnId = subnode_value(i, "FKColumn")

				pk_column = self.pk_table.findColumn(pkColumnId)
				fk_column = self.fk_table.findColumn(fkColumnId)

				self.pk_columns.append(pk_column)
				self.fk_columns.append(fk_column)

				fk_column.is_fk = True
				fk_column.pk_column = pk_column



	def __repr__(self):
		return "<Reference(name='%s')>"  % (self.name)

	def dump(self):
		print str(self)


class DbModel():

	tables = None
	references = None
	views = None

	def __init__(self):
		self.tables = []
		self.references = []
		self.views = []

	def findTable(self, id):
		for i in self.tables:
			if(i.id == id):
				return i

		raise Exception, "Database model is corrupted. Couldn't find table with id: " + id

	def build(self,xmlRoot):

		tables = xmlRoot.getElementsByTagName('Tables')[0]

		for i in tables.childNodes:
			if(i.nodeType == Node.ELEMENT_NODE):
				t = Table()
				t.dbModel = self
				t.build(i)
				self.tables.append(t)

		references = xmlRoot.getElementsByTagName('References')[0]

		for i in references.childNodes:
			if(i.nodeType == Node.ELEMENT_NODE):
				r = Reference()
				r.dbModel = self
				r.build(i)
				self.references.append(r)

	def dump(self):
		print "Model"
		for i in self.tables:
			i.dump()

#################################################################

### SQLAlchemy model. 

def to_camelcase(s):
    return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), s)

def sa_class_name(sql_name):
		return "".join([x.capitalize() for x in sql_name.split("_")])

def sa_property_name(sql_name):
		return sql_name.lower()

class SaColumn():
	name = None
	column_name = None
	python_type = None
	is_pk = False
	description = None
	fk_table_column = None
	is_deferred = False

	def emit(self, emiter):

		extraParams = ""

		if (self.fk_table_column != None):
			extraParams += ", ForeignKey('%s')" % (self.fk_table_column)

		if (self.is_pk):
			extraParams += ", primary_key = True"

		emiter.comment(self.description)

		if(self.is_deferred):
			template = "%s = deferred(Column('%s', %s%s))"
		else:
			template = "%s = Column('%s', %s%s)"			

		emiter.emit(template % (self.name, self.column_name, self.python_type, extraParams))


class SaRelationship():
	role = ""
	class_name = ""
	backref = ""
	foreign_keys = ""

	def emit(self, emiter):
		if(self.backref == None):
			emiter.emit("%s = relationship('%s', foreign_keys=%s)" % (self.role, self.class_name, self.foreign_keys))
		else:
			emiter.emit("%s = relationship('%s', backref='%s',foreign_keys=%s)" % (self.role, self.class_name, self.backref,self.foreign_keys))



class SaTable():
	description = ""	
	name = None
	columns = None
	relationships = None

	def __init__(self):
		self.columns = []
		self.relationships = []

	def emit(self, emiter):
		emiter.comment("name " + self.name)


class SaClass():

	name = None
	table_name = None
	description = None
	columns = None
	relationships = None

	def __init__(self):
		self.columns = []
		self.relationships = []


	def emit(self,emiter):
		emiter.comment(self.description)
		emiter.emit("class %s (Base):" % (self.name))
		emiter.indent()
		emiter.emit('__tablename__ = "%s"' % (self.table_name))

		for c in self.columns:
			c.emit(emiter)

			
 		if(len(self.relationships) > 0):
			emiter.nl()
			for r in self.relationships:
				r.emit(emiter)

		emiter.deindent()


class SaModel():

	elements = None

	def __init__(self):
		self.elements = []

	def emit(self, emiter):
		emiter.comment("-*- encoding: utf-8 -*-")
		emiter.comment("begin")
		emiter.nl()
		emiter.emit("import sqlalchemy")
		emiter.emit("from sqlalchemy import create_engine")
		emiter.emit("from sqlalchemy.ext.declarative import declarative_base")
		emiter.emit("from sqlalchemy import Column, Integer, BigInteger,String, ForeignKey, Unicode, Binary, LargeBinary, Time, DateTime, Date, Text, Boolean")
		emiter.emit("from sqlalchemy.orm import relationship, backref, deferred")
		emiter.emit("from sqlalchemy.orm import sessionmaker")
		emiter.nl()
		emiter.emit("Base = declarative_base()")
		emiter.vspace()

		for t in  self.elements:
			t.emit(emiter)
			emiter.nl()

		emiter.comment("end")

####################################################################################

## FIXME add type mapping for every supported database engine
## this is a temporary solution

string_sql_types = set(["varchar","char","nchar","nvarchar"])
integer_sql_types = set(['int', 'int4','integer'])
big_integer_sql_types = set(['numeric','decimal'])
blob_sql_types = set(['oid', 'blob'])
clob_sql_types = set(['text', 'clob'])
datetime_sql_types = set(['datetime'])
timestamp_sql_types = set(['timestamp'])
date_sql_types = set(['date'])
bool_sql_types = set(['bool'])


class Generator():

	root = None
	dbModel = None
	saModel = None
	
	def parse(self,xmlString):
		self.root = minidom.parseString(xmlString)

	def guessType(self, type):

		 

		type = type.lower()

		# strip type parameters 'varchar(100)' -> 'varchar'
		type = type.split('(')[0];

		if(type in string_sql_types):
			return "Unicode"

		if(type in integer_sql_types):
			return "Integer"

		if(type in big_integer_sql_types):
			return "BigInteger"

		if(type in blob_sql_types):
			return "LargeBinary"

		if(type in clob_sql_types):
			return "Text"

		if(type in datetime_sql_types):
			return "DateTime"

		if(type in date_sql_types):
			return "Date"

		if(type in timestamp_sql_types):
			return "Time"
		
		if(type in bool_sql_types):
			return "Boolean"

		return None


	def is_deferred(self, python_type):
		
		if(python_type == "Text" or python_type == "LargeBinary"):
			return True

		return False	


	def processColumn(self, column):
		res = SaColumn()
		res.name = sa_property_name(column.name)
		res.column_name = column.name
		res.python_type = self.guessType(column.sql_type)
		res.description = column.description
		res.is_pk = column.is_pk

		if (column.is_fk):
			res.fk_table_column  = column.pk_column.column_with_table_name()

		if(res.python_type == None):
			warn = "Unknown SQL type: '%s' " % (column.sql_type)
			#print column.table.name, column.name, warn
			res.description += warn 
			res.python_type = "String"

		res.is_deferred = self.is_deferred(res.python_type)

		return res

	def processReference(self, reference):


		# FIXME add support for multiple columns reference
		if(len(reference.fk_columns) > 1):
			return None

		res = SaRelationship()
		role = reference.fk_role
		backref = reference.pk_role
		sa_property = reference.fk_columns[0].name

		if(role == ""):
			role = reference.pk_table.name

		if(backref == ""):
			backref = None
		else:
			backref = reference.fk_table.name + "_" + backref

		res.role = sa_property_name(role)
		res.class_name = sa_class_name(reference.pk_table.name)

		if (backref == None):
			res.backref = None
		else:
			res.backref = sa_property_name(backref)

		res.foreign_keys = sa_property_name(sa_property)

		return res

	def processTable(self, table):

		res = SaClass()

		res.name = sa_class_name(table.name)
		res.table_name = table.name
		res.description = table.description

		for i in table.columns:
			res.columns.append(self.processColumn(i))

		for i in table.fk_references:
			r = self.processReference(i)
			if(r != None):
				res.relationships.append(r)

		return res


	def process(self):
		self.dbModel = DbModel()
		self.dbModel.build(self.root)

		self.saModel = SaModel()

		for i in self.dbModel.tables:
			self.saModel.elements.append(self.processTable(i))

	
	def code(self):
		emiter = CodeEmiter()
		self.saModel.emit(emiter)
		return emiter.code()


def generate(xmlFile, pyFile):
	inf = open(xmlFile,"r")
	xml=inf.read()

	g = Generator();
	g.parse(xml)
	g.process();

	outf = open(pyFile, "w")
	outf.write(g.code())
	outf.close()

################################################################################


def main(argv):
	inputfile = 'model.xml'
	outputfile = 'model.py'

	try:
		opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print 'vertabelo_sqlalchemy.py -i <inputfile> -o <outputfile>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'vertabelo_sqlalchemy.py -i <inputfile> -o <outputfile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg

	generate(inputfile,outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])

