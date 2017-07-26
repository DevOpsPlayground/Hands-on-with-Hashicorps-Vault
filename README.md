# DevOps Playground #13 - HashiCorp's Vault
All the content needed for the DevOps Playground Meetup on Vault (13) will be worked on here.

# Infrastructure

The AWS instances provided are simple ubuntu machines, a few things have been done on them:
1. MySQL
2. The Vault binary is in the PATH
3. The Envconsul binaryu is the PATH

# Application  
The application is a simple python script that populates a mysql table with data from a text file and read one out, at random.
It requires knowledge about the database :
1. host : where it is
2. user : username to auth to the db
3. passwd : password
4. db : database name

As we start all these values are hardcoded in the mysql function call, in view_base.py

# Work
## 0 -  Complete the setup

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

The next step is obviously to set up the Vault server. The Vault binary is already present on the machine, but the server needs to be started.

Since we are not running a production-grade environment, we will use Vault in its DEV mode, making our life simpler.

To start Vault as DEV simply use the command below:   
`vault server -dev &`

As we will use them later, let's get the token and the address from the logs and store it in an env variable:  
`export VAULT_TOKEN= <token>`
`export VAULT_ADDR= <addr>``

##  1 - Intro to vault

For what we are going to use Vault for, we can assimilate it as an encrypted key/value store, but keep in mind that it can go much further than that.   

A secret needs to be stored in vault before being shared with an application.

A few ways to make a secret available to the application:  
1. Host env var  
2. Sub-shell env var (env consul)  
3. API call

We will see all three here.

### 1.1 - Confirm we have installed vault properly
vault status should indicated that Vault is operational :

`vault status`

you should get something like that :


### 1.2 - Write our first secret

Vault stores secrets in secret backend. The generic secret backend endpoint that we will use is */secret*

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

`python base.py`  

At the moment the application has all values hardcoded, but it works as expected (displaying a random fruit name)

The plan is to gradually remove the hardcoded values from the application, and reference variables.

### 2.2 - Get environment variable from the application
Since we have setup some both `VAULT_ADDR` and ` VAULT_TOKEN` environment variables, our python app should be able to access them.


The following code retrieves the variables from the environment, display them on the screen.
```python
def getEnvVar():
    global vault_addr
    global vault_token

    vault_token = str(os.environ['VAULT_TOKEN'])
    vault_addr = str(os.environ['VAULT_ADDR'])

    print "VAULT ADDR :", vault_addr
    print "VAULT TOKEN :", vault_token
    print "\n"

    return vault_addr, vault_token
```

Add this code in the .py script.  

The call to the function needs to be added too, at the bottom of the file.  
`vault_addr, vault_token = getEnvVar()`

### 2.3 -  Run the application again
The output of the application should now include the values of both `VAULT_ADDR` and ` VAULT_TOKEN`

Since we haven't touched the database details the random fruit is still displayed.

`python base.py`

### 2.4 - Summary - Secret as environment variables

## 3 - Have Vault store the VAULT_ADDR, Share it with Envconsul

It is understandable to try to avoid storing secret or application specific variable at the environment level.

Envconsul is another HashiCorp tool made specifically for this purpose. It allows vault secret to be injected in a sub-shell running the application.

### 3.1 - Write VAULT_ADDR as a secret

In this case, EnvConsul will work with secrets, so we need to store our VAULT_ADDR into Vault.  
`vault write secret/VAULT ADDR=http://localhost:8200`

Confirm the secret has been written by reading it.

### 3.2 - Call EnvConsul to inject it into the sub-shell


`vim config` :

```ruby
vault {
    address = "http://127.0.0.1:8200"
    token   = "<ROOT TOKEN>"
    renew   = false
    secret {
      no_prefix = true
    }  
}
```

`envconsul -config="./config" -secret="secret/VAULT" python web.py`


The behavior of the application should have been the exact same as in Step 2:
1. Envconsul injected the secret as an env variable, with the same namae as before
2. the function getEnvVar() should have been able to pick it up tool
3. If you remove the VAULT_ADDR env var (` unset VAULT_ADDR`) from your host environment. You should still be able to run the above command seamlessly.


### 3.3 - Summary - Envconsul


## 4 - Use the API to read secret

### 4.1 - Intro to Vault's API
Vault has a rich API, allowing us to do almost anything with our secret.
The API endpoint looks like that `$VAULT_ADDR/v1/secret/...`.
In our case, all we want will be to read secret.   
By default, on generic secret,  a simple HTTP GET request is a read operation.

Note: we have to authenticate with our token at **each** HTTP requests puting the token in a header.

This is what an API call to read our secret/website looks like :

`curl -H "X-Vault-Token: <TOKEN>" http://localhost/v1/secret/website`

The output is in a JSON format, which contain our secrets.


### 4.2 - Store the Database credentials in Vault

The database needed by the application requires 4 values :
1. host = localhost
2. user = root
3. password = root
4. db=playground

Let's go ahead and write those key/value pairs under secret/database  
`vault write secret/database host=localhost user=root password=root db=playground`

Confirm the writing has been successful by reading them.

### 4.3 - Modify the code to call the API and read the credentials

If all the previous steps were successful, then the application should already be able to read VAULT_ADDR and VAULT_TOKEN, and the database connection information should be in Vault ready to be read.

#### 4.3.1 - Make a call to the Vault API in Python
In python, this is how you would make an API call, and passing headersto it:
```python
headers = '{X-Vault-Token:', vault_token,'}'
Resp = requests.get(vault_addr + "/v1/secret/database", headers = {"X-Vault-Token": vault_token})

```
Here, for simplicity, we have hardcoded the secret's path. More error catching should of course be added to it. see below.


#### 4.3.2 - Write the function to get the database credentials

The function below is making an PAI call to VAULT using the token and addr we already have, to read the database information we stored on Vault. Then we simply check the HTTP return code, to confirm the success of the request. Finally, we display and store the credentials.

```python
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
```

`envconsul -config="config" -secret="secret/database" python base.py`


# Reading Material
