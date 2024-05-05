## "Botfarm" fastapi service

This web-service is designed to simulate the workflow of a bot-farm. The service provides access to bot database which allows an admin to create, lock and retrieve available bots.

The service is developed using FASTapi, SQLAlchemy, JWT authentication and Docker. It can also be deployed in minikube.

In order to start a web-server you're first required to create an .env file with the following fields:

- DB_URL (postgres url of the database in the format "postgresql+asyncpg://*username*:*password*@*host*:*port*/*db-name*")
- TEST_DB_URL (postgres url of the database for testing)
- DB_URL_LOCAL (postgres url of the database for local development)
- TEST_DB_URL_LOCAL (postgres url of the database for local testing)
- POSTGRES_DB (name of the database)
- POSTGRES_TEST_DB (name of the test database)
- POSTGRES_USER (name of the postgres user)
- POSTGRES_PASSWORD (password of the postgres user)
- POSTGRES_HOST (postgres host)
- FIRST_DB_ADMIN_LOGIN (desired login for the first admin)
- FIRST_DB_ADMIN_PASSWORD (desired password for the first admin)
- SECRET_KEY (secret key in base64 for JWT token)

### Afterwards, if you wish to start the project locally:
- change the DB_URL etc. to corresponding LOCAL variables in the code
- run
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicord main:app
```
- send a POST request on /superuser to create a first admin
- get a JWT token for the first admin
- explore more endpoints on /docs

### If you wish to start a service in a docker container:
- Make sure you have docker installed
- run
```
docker-compose up --build
```
- send a POST request on /superuser to create a first admin
- get a JWT token for the first admin
- explore more endpoints on /docs


### Pytests tests are available

run locally: ```pytest```

in a docker container: ```docker-compose exec fastapi-app pytest```