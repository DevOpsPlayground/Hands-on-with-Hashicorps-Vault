import os, MySQLdb, requests, logging, json

mysql = ""

def getEnvVar():
    global vault_addr
    global vault_token
    vault_token = str(os.environ['VAULT_TOKEN'])
    vault_addr = str(os.environ['VAULT_ADDR'])
    print vault_addr," --- ", vault_token
    print "\n"
    return vault_addr, vault_token

def parseDB(host, db, user, passwd):
    #connect to the db existing on the machine
    #db = MySQLdb.connect(host="localhost", user="root", passwd="root",  db="Playground")
    global mysql
    mysql = MySQLdb.connect(host=host, user=user, passwd=passwd,  db=db)
    cur = mysql.cursor()
    # Read all from main tables
    f=open('list.txt','r')
    for line in f:
        cur.execute("INSERT INTO main (id) VALUES (\'"+line+"\')")

    # cur.execute("SELECT * FROM main")
    # for row in cur.fetchall():
    #     print row[0]
    mysql.close()

def getDBCredsFromVault(vault_addr, vault_token):
    headers = '{X-Vault-Token:', vault_token,'}'
    Resp = requests.get(vault_addr + "/v1/secret/database", headers = {"X-Vault-Token": vault_token})

    # 200 = OK, other = NOK
    if(Resp.ok):
        secret = json.loads(Resp.content)
        # print secret
        print "host : ", secret["data"]["host"]
        host = secret["data"]["host"]
        print "database : ", secret["data"]["db"]
        db = secret["data"]["db"]
        print "user : ", secret["data"]["user"]
        user = secret["data"]["user"]
        print "password : ", secret["data"]["passwd"]
        passwd = secret["data"]["passwd"]
        print "\n"
    else:
        Resp.raise_for_status()
    return host, db, user, passwd

#### main
vault_addr, vault_token = getEnvVar()
host, db, user, passwd = getDBCredsFromVault( vault_addr, vault_token)
parseDB(host, db, user, passwd)
