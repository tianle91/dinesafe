# Dinesafe
[![ci](https://github.com/tianle91/dinesafe/actions/workflows/ci.yaml/badge.svg)](https://github.com/tianle91/dinesafe/actions/workflows/ci.yaml)

Check out [dinesafe.tchen.xyz](http://dinesafe.tchen.xyz)

## Deploy
Fill out the following secrets
- `.streamlit/secrets.toml`
- `api.env` (you need a decently complex api key since it's insecure)
- `mysql.env` (optional - mysql is local only)

Then run `docker-compose up`.
