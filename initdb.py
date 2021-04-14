import os
import csv
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy import DateTime, Float, Integer, String

"""
Create a variable name meta to store a collection of metadata entities
"""
meta = MetaData()

"""
using an environment variable for storing the details of our database connection 
(which is use to keep the login and password of our database outside of ourcode)
"""
os_env_db_url = os.environ.get('DATABASE_URL', '')

connection = os_env_db_url or "sqlite:///db.sqlite"

engine = create_engine(connection)

"""
Add the database if the table is not exist
"""
if not engine.has_table("breweries"):
    print("Creating Table")

    """
    The usual way to issue CREATE is to use create_all() on the MetaData object. 
    This method will issue queries that first check for the existence of each individual table, 
    and if not found will issue the CREATE statements:
    """
    new_table = Table(
        'breweries', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String),
        Column('brewery_type', String),
        Column('address', String),
        Column('state', String),
        Column('phone', String),
        Column('website_url', String),
        Column('country', String),
        Column('region', String),
        Column('division', String),
        Column('longitude', Integer),
        Column('latitude', Integer)
    )

    meta.create_all(engine)
    
    print("Table created")

    """
    Let's read in the csv data and put into a list to read into
    our newly created table
    """
    seed_data = list()

    with open('data/breweries_clean.csv', newline='') as input_file:
        reader = csv.DictReader(input_file)       #csv.reader is used to read a file
        for row in reader:
            seed_data.append(row)
    
    """
    With our newly created table let's insert the row we've read in
    and with that we're done
    """
    with engine.connect() as conn:
        conn.execute(new_table.insert(), seed_data)

    print("Seed Data Imported")
else:
    print("Table already exists")

print("initdb complete")