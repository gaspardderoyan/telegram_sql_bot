import psycopg2
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

conn = psycopg2.connect(
    user= os.getenv('DB_USER'),
    password= os.getenv('DB_PASSWORD'),
    host= os.getenv('DB_HOST'),
    port="13645",
    database="postgres")

cursor = conn.cursor()

# Query the database
cursor.execute("SELECT * FROM Habits;")
