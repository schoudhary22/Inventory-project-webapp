# app.py

import os
import urllib
from flask import Flask, render_template, request
from sqlalchemy import create_engine, Column, String, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Database configuration using environment variables
DATABASE_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': os.environ.get('DB_SERVER'),
    'database': os.environ.get('DB_NAME'),
    'username': os.environ.get('DB_USERNAME'),
    'password': os.environ.get('DB_PASSWORD'),
}

# Ensure that all required environment variables are set
for key, value in DATABASE_CONFIG.items():
    if value is None:
        raise ValueError(f"Environment variable {key} is not set.")

# Build the connection string
connection_string = (
    'DRIVER=' + DATABASE_CONFIG['driver'] + ';'
    'SERVER=' + DATABASE_CONFIG['server'] + ';'
    'DATABASE=' + DATABASE_CONFIG['database'] + ';'
    'UID=' + DATABASE_CONFIG['username'] + ';'
    'PWD=' + DATABASE_CONFIG['password'] + ';'
    'Encrypt=yes;'
)

# Encode the connection string
params = urllib.parse.quote_plus(connection_string)

# Create the SQLAlchemy engine
engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

# Create a base class for declarative class definitions
Base = declarative_base()

# Define the Product model
class Product(Base):
    __tablename__ = 'Products'
    ProductID = Column(String(10), primary_key=True)
    ProductName = Column(String(100))
    Category = Column(String(50))
    QuantityInStock = Column(Integer)
    Price = Column(Numeric(10, 2))

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

@app.route('/', methods=['GET', 'POST'])
def index():
    session = Session()
    products = None
    search_term = None
    if request.method == 'POST':
        if 'search' in request.form:
            # User clicked the Search button
            search_term = request.form.get('product_id')
            if search_term:
                products = session.query(Product).filter(Product.ProductID == search_term).all()
        elif 'show_all' in request.form:
            # User clicked the Show All Products button
            products = session.query(Product).all()
    return render_template('index.html', products=products, search_term=search_term)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
