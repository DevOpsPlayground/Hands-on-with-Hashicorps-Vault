import os, MySQLdb, requests, json


mysql = ""

def populateDB():
    #connect to the db existing on the machine
    global mysql
    mysql = MySQLdb.connect(host="localhost", user="root", passwd="root",  db="Playground")
    cur = mysql.cursor()
    # Read all from main tables
    f=open('list.txt','r')
    for line in f:
        cur.execute("INSERT INTO main (id) VALUES (\'"+line+"\')")

    mysql.commit()
    mysql.close()

def getRandomFruit():
    global mysql
    mysql = MySQLdb.connect(host="localhost", user="root", passwd="root",  db="Playground")
    cur = mysql.cursor()
    cur.execute("SELECT * FROM main ORDER BY RAND() LIMIT 1")
    fruit = cur.fetchall()
    print fruit[0][0]

#### main
populateDB()
getRandomFruit()
