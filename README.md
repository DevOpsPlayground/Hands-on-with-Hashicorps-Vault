# devopsplayground13-vault
All the content needed for the DevOps Playground Meetup on Vault (13) will be worked on here.

## Step 0 - Setting up Vault Server
vault server -dev
export VAULT_ADD=http://127.0.0.1:8200
copy root token
 

## Step 1 - our first secret
vault write secret/application url= ecs-digital.co.uk
vault read  secret/application
vault read -field=url secret/application


## Step 2 - inject our first secret

vim config
  vault {
    address = "http://127.0.0.1:8200"
    token   = "<ROOT TOKEN>" // May also be specified via the envvar VAULT_TOKEN
    renew   = false
  }

envconsul -config="config" -secret="secret/application" python app.py
