import mysql.connector

connection = mysql.connector.connect(
    host='nums.mysql.pythonanywhere-services.com',
    user='nums',
    password='numeriz44',
    database='secure_healthap'
)

if connection.is_connected():
    print("Connection successful!")
else:
    print("Connection failed.")