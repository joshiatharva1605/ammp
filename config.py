import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="ammp_db"
)

cursor = db.cursor(dictionary=True)