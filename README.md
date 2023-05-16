# Dinesafe

Check out [dinesafe.tchen.xyz](http://dinesafe.tchen.xyz)

## Deploy
Fill out the following secrets
- `.streamlit/secrets.toml`
- `api.env` (you need a decent api key since the api is public)
- `mysql.env` (optional - mysql is local only)

Then run `docker-compose up`.

### Deploy api only
This separates the mysql container from the api container so that any updates can be made independently.
`docker network create mysql`
`docker run -d -e MYSQL_ROOT_PASSWORD=mysql_root_password --network=mysql --name mysql mysql`
`docker-compose -f docker-compose-api.yaml up -d`
