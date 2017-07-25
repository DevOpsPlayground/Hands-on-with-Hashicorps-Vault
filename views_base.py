import os, MySQLdb, requests, json


mysql = ""
vault_addr = ""
vault_token = ""
host = ""
db = ""
user = ""
passwd = ""

def populateDB():
    #connect to the db existing on the machine
    global mysql
    mysql = MySQLdb.connect(host="localhost", user="root", passwd="root",  db="Playground")
    cur = mysql.cursor()
    # Read all from fruits tables
    f=open('list.txt','r')
    for line in f:
        cur.execute("INSERT INTO fruits (name) VALUES (\'"+line+"\')")

    mysql.commit()
    mysql.close()

def getRandomFruit():
    global mysql
    mysql = MySQLdb.connect(host="localhost", user="root", passwd="root",  db="Playground")
    cur = mysql.cursor()
    cur.execute("SELECT * FROM fruits ORDER BY RAND() LIMIT 1")
    fruit = cur.fetchall()
    print fruit[0][0]

#### Main
populateDB()
getRandomFruit()
