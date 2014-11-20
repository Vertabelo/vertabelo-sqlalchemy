vertabelo-sqlalchemy example
============================

Files:

1. example.xml        - database model as an Vertabelo XML file (exported from Vertabelo)
2. example_create.sql - DDL that creates schema (generated by Vertablo)
3. example_data.sql   - some test data (generated by hand)
4. example.db         - sqlite database file (generated by sqlite)
5. example_model.py   - SQLAchemy mapping classes (generated by vertabelo_sqlalchemy, see prepare.sh file)
6. prepare.sh         - cleans database, regenerates classes
7. run-example.py     - a simple application  

Usage:

Call:

 ./run-example.py


