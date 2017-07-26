# DevOps Playground #13 - HashiCorp's Vault
All the content needed for the DevOps Playground Meetup on Vault (13) will be worked on here.

# Infrastructure

The AWS instances provided are simple ubuntu machines, a few bits have been configured :
1. MySQL
2. The Vault binary is in the PATH
3. The Envconsul binary is the in PATH
4. The Github repository for this meetup has been cloned locally


# Application  
The application is a simple python script that populates a mysql table with data from a text file and reads one out, at random.

It requires knowledge about the database :
1. host : where it is
2. user : username to auth to the db
3. passwd : password
4. db : database name

As we start all these values are hardcoded in the mysql function call, in app.py

# Work
## 0 -  Complete the setup

SSH into the machine using the IP provided to you.

As we are using the standard AWS LINUX AMI, the user is ec2-user**

There should be a folder called *devopsplayground13-vault* in the ec2-user's home. Go into it.
`cd devopsplayground13-vault`


### 0.1 - Configure database

First, for the sake of simplicity, we'll use a SQWL script to create the database and table. The application will then use those.

The Mysql server has already been configured with credentials, so username: **root** and password: **root** will work.

In the same folder :  
`mysql -u root -p < setup.sql`

When prompter fro a password, use **root**

If no error has arisen, the database should be readuy to use.


### 0.2 - Setting up Vault Server

The next step is to set up the Vault server. The Vault binary is already present on the machine, but the server needs to be started.

Since we are not running a production-grade environment, we will use Vault in its DEV mode, making our life simpler.

To start Vault as DEV simply use the command below:   ˜
`vault server -dev &`

As we will use them later, let's get the token and the address from the logs and store it in an env variable:  
`export VAULT_TOKEN= <token>`  
`export VAULT_ADDR= <addr>`

##  1 - Intro to vault

For what we are going to use Vault for, we can assimilate it as an encrypted key/value store, but keep in mind that it can go much further than that.   

A secret needs to be stored in vault before being shared with an application.

Here are a few ways to make a secret available to an application1.
1. Host env var  
2. Sub-shell env var (env consul)  
3. API call
4. Consul template


We will see all three here.

### 1.1 - Confirm we have installed vault properly
vault status should indicated that Vault is operational :

`vault status`

you should get something like that :

˜˜ 
### 1.2 - Write our first secret

Vault stores secrets in a secret backend. The generic secret backend endpoint that we will use is */secret*

We will then use a format similar to : `vault write secret/secret_name key=value`  

Let's create our first secret :
`vault write secret/website url=ecs-digital.co.uk`  
To confirm our secret has been written:
`vault read  secret/website`  
if you get your secret back, bravo.

Note: you can write several key/value to a secret:  
`vault write secret/website url=ecs-digital.co.uk page=JoinUs`  
In this case, you can select the exact field you want to read:  
`vault read -field=url secret/application`


## 2 - Use environment variable from the application


### 2.1 - Run the application a first time

`python app.py`  

At the moment the application has all values hardcoded, but it works as expected (displaying a random fruit name)

The plan is to gradually remove the hardcoded values from the application, and reference variables.

### 2.2 - Get environment variable from the application
Since we have setup both VAULT_ADDR and VAULT_TOKEN environment variables, our python app should be able to access them.


The following code retrieves the variables from the environment and displays them on the screen.
```python
def getEnvVar():
    global vault_addr
    global vault_token

    vault_token = str(os.environ['VAULT_TOKEN'])
    vault_addr = str(os.environ['VAULT_ADDR'])

    print "---FROM ENV---"
    print "VAULT ADDR :", vault_addr
    print "VAULT TOKEN :", vault_token
    print "\n"

```

Add this code in the .py script.  

The call to the function needs to be uncommented at the bottom of the file.  
`getEnvVar()`

### 2.3 -  Run the application again
The output of the application should now include the values of both `VAULT_ADDR` and ` VAULT_TOKEN`

Since we haven't touched the database details the random fruit is still displayed.

`python app.py`

## 3 - Write Database information in VAULT

It is understandable to try to avoid storing secret or application specific variable at the environment level.

Envconsul is another HashiCorp tool made specifically for this purpose. It allows vault secret to be injected in a sub-shell running the application.

### 3.1 - Store the Database credentials in Vault

The database needed by the application requires 4 values :
1. host = localhost
2. user = root
3. password = root
4. db=playground

Let's go ahead and write those key/value pairs under secret/database  
`vault write secret/database host=localhost user=root password=root db=playground`

Confirm the writing has been successful by reading them.

###  3.2 - Modify the code to display the EnvConsul values

Add the following code to the script:

```python
def getVarFromEnvconsul():

    db = str(os.environ['db'])
    host = str(os.environ['host'])
    user = str(os.environ['user'])
    passwd =str(os.environ['password'])

    print "---FROM ENVCONSUL---"
    print "DB :", db
    print "Host :", host
    print "User :", user
    print "Password :", passwd

    print "\n"
```

### 3.3 - Call EnvConsul to inject it into the sub-shell


`vim config` :

```ruby
secret {
     path = "secret/database"
     no_prefix = true
}
vault{
  renew = false
}

```

`envconsul -config="./config" python app.py`


## 4 - Use the API to read secret

### 4.1 - Intro to Vault's API
Vault has a rich API, allowing us to do almost anything with our secret.
The API endpoint looks like that `$VAULT_ADDR/v1/secret/...`.
In our case, all we want will be to read a secret.  
By default, on generic secret,  a simple HTTP GET request is a read operation.

Note: we have to authenticate with our token at **each** HTTP requests putting the token in a header.

This is what an API call to read our secret/website looks like :

`curl -H "X-Vault-Token: $VAULT_TOKEN" -X GET http://localhost:8200/v1/secret/website`

The output is in a JSON format, which contain our secrets.


### 4.2 - Modify the code to call the API and read the credentials

If all the previous steps were successful, then the application should already be able to read VAULT_ADDR and VAULT_TOKEN, and the database connection information should be in Vault ready to be read.

#### 4.2.1 - Make a call to the Vault API in Python
In python, this is how you would make an API call, and passing headers to it:
```python
headers = '{X-Vault-Token:', vault_token,'}'
Resp = requests.get(vault_addr + "/v1/secret/database", headers = {"X-Vault-Token": vault_token})

```
Here, for simplicity, we have hardcoded the secret's path. More error catching should of course be added to it. see below.


#### 4.2.2 - Write the function to get the database credentials

The function below is making an PAI call to VAULT using the token and addr we already have, to read the database information we stored on Vault. Then we simply check the HTTP status code, to confirm the success of the request. Finally, we display and store the credentials.

```python

def getDBCredsFromVault():
    global vault_addr
    global vault_token
    headers = '{X-Vault-Token:', vault_token,'}'
    Resp = requests.get(vault_addr + "/v1/secret/database", headers = {"X-Vault-Token": vault_token})

    # 200 = OK, other = NOK
    if(Resp.ok):
        secret = json.loads(Resp.content)
        db = secret["data"]["db"]
        user = secret["data"]["user"]
        passwd = secret["data"]["password"]
        host = secret["data"]["host"]

        print "--- FROM VAULT API---"
        print "database : ", secret["data"]["db"]
        print "user : ", secret["data"]["user"]
        print "host : ", secret["data"]["host"]
        print "password : ", secret["data"]["password"]
        print "\n"
    else:
        Resp.raise_for_status()
```

Don't forget to uncomment the function call at the bottom of the file !

`envconsul -config="./config" python app.py`

### Modify the MySQL call to use the variables

In the functions `populateDB()` and `getRandomFruit()`, let's replace the original mysql calls by :

```python
mysql = MySQLdb.connect(host=host, user=user, passwd=password,  db=database)
```

You also need to set as global these variables in the functions `getDBCredsFromVault`, `populateDB` and `getRandomFruit` in order to make the environment variables accessible:
```
    global host
    global db
    global passwd
    global user
```

Now the application is operating fully on secret from Vault. let's run the application a final time to confirm:  
`envconsul -config="./config" python app.py`

# Reading Material
