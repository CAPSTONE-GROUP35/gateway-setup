from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

def getPasswordHash(user):
    cursor.execute("SELECT * FROM user WHERE Username=?",[user])
    records = cursor.fetchall()
    print("Total rows are: ",len(records))
    print("Printing each row")
    for row in records:
        print("ID: ",row[0])
        print("username: ", row[1])
        print("password: ", row[2])
        print("\n")

def hashPassword(password):
    result=generate_password_hash(password, method='scrypt')
    print(result)

def checkPasswordHash(password, user):
    cursor.execute("SELECT password FROM user WHERE Username=?",[user])
    records = cursor.fetchall()
    for row in records:
        user_result = row[0]       
    
    if(check_password_hash(user_result, password)):
        print("The hashed passwords match!")
    else:
        print("The hashed passwords DO NOT match!")

