# devopsplayground13-vault
All the content needed for the DevOps Playground Meetup on Vault (13) will be worked on here.

## Infrastructure 

The AWS instances provided are simple ubuntu machines, a few things hace been done on them: 
1. MySQL
2. The Vault binary is in the PATH
3. The Envconsul binaryu is the PATH

## Application Architecture 
The application is a simple python script that populates a mysql table with data from a text file and read one out, at random.



## Step 0 -  Complete the setup 

### Configure database 


### Setting up Vault Server
`vault server -dev`

`export VAULT_ADD=http://127.0.0.1:8200`

`export VAULT_TOKEN= <token>`


## Step 1 - our first secret
`vault write secret/application url= ecs-digital.co.uk`

`vault read  secret/application`

`vault read -field=url secret/application`

## Step 2 - inject our first secret with EnvConsul

vault write secret/database/credentials/root password=root

`vim config` :
```ruby
vault {
    address = "http://127.0.0.1:8200"
    token   = "<ROOT TOKEN>" // May also be specified via the envvar VAULT_TOKEN
    renew   = false
}
```

`envconsul -config="config" -secret="secret/database/credentials/root" python web.py`

## Step 3 retrieve Env var from the code 
copy paste

```python
def getEnvVar():
    global vault_addr
    global vault_token
    vault_token = str(os.environ['VAULT_TOKEN'])
    vault_addr = str(os.environ['VAULT_ADDR'])
    print vault_addr," --- ", vault_token
    print "\n"
    return vault_addr, vault_token
```

## Step 4 Store Credentials on vault
vault write secret/database host=localhost db=playground user=root

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

`envconsul -config="config" -secret="secret/database/credentials/root" python web.py`


## Step 5 



