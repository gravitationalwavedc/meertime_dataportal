# MeerTime

## About
The MeerTime project is a five-year program on the MeerKAT array by an international consortium that will regularly time over 1000 radio pulsars to perform tests of relativistic gravity, search for the gravitational wave signature induced by supermassive black hole binaries in the timing residuals of millisecond pulsars, explore the interiors of neutron stars through a pulsar glitch monitoring programme, explore the origin and evolution of binary pulsars, monitor the swarms of pulsars that inhabit globular clusters and monitor radio magnetars. MeerTime will complement the TRAPUM project and time pulsars TRAPUM discovers in surveys of the galactic plane, globular clusters and the galactic centre. In addition to these primary programmes, over 1000 pulsars will have their arrival times monitored and the data made immediately public.

This application provides a ReactJS frontend for access to the MeerTime project data for authenticated astronomers and provides a Django powered graphQL API.


## Requirements
* Python >= 3.8

### To run on your local machine
* MySQL server

### To run in Docker
* Docker
* Docker Compose


## Setup: to run on your local machine

### Running the Django development server

1. Clone the repository and move into `backend` directory.

2. Install python packages using [python poetry](https://python-poetry.org/):
To install `poetry`, follow the instructions on their website. As of Nov. 24 the instructions were to install `pipx`, to then run `pipx install poetry`. There is no need to create an environment for this project as `poetry` will take care of it. Instead, add `poetry run` before running any Python scripts from this project.

Run `poetry install --no-dev` for minimum install. This only installs required production packages.
Run `poetry install` to also install development packages such as testing tools.

3. Prepare the environment running `cp .env.template .env`. Do not change any fields to `backend/.env` yet.

4. Install `postgresql` with `sudo apt install postgresql postgresql-contrib libpq-dev`.

If you have a Mac, install with [brew](https://docs.brew.sh/Installation): `brew install postgresql libpq redis`. You also need to change `REDIS_SERVER=redis://localhost:6379` in your `backend/.env` file. 

5. Create the `postgresql` database and the `meertime` database user using the following commands (filling in the `$` value and copying it in your `backend/.env`).
If you have a Mac, replace the first line with `psql postgres`. You are opening a postgreSQL shell in database `postgres` as your shell user.
```
sudo -u postgres psql

CREATE DATABASE meertime; CREATE USER meertime WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD'; ALTER ROLE meertime SET client_encoding TO 'utf8'; ALTER ROLE meertime SET default_transaction_isolation TO 'read committed'; ALTER ROLE meertime SET timezone TO 'UTC'; ALTER USER meertime CREATEDB; \q
```
The last command is to be able to run `pytest`. Also, change `POSTGRES_DATABASE=meertime` and `POSTGRES_USER=meertime` in your `backend/.env`.

To then load a local copy of the database, ask ADACS for a copy (here named `prd.meertime.sql`) and do: `pg_restore -U meertime -d meertime -h localhost -p 5432 -v prd.meertime.sql`. You can check this step was successful using the postgreSQL shell (see 5.) by running `\du` and `\l`.

6. Migrate all the changes to the database if any, so it is in the correct format: `poetry run python manage.py migrate`.

7. Create Django superuser. Execute the following in the `backend` folder: `poetry run python manage.py createsuperuser` to create a Django admin that will be able to log in on the Django admin page: http://localhost:8000/admin. 

8. Start the development server: run `poetry run python manage.py runserver` and open the [Django development server](http://localhost:8000).

9. Run tests on the backend development server to check it is all working. In the `backend` folder run: `poetry run pytest`.

### Starting the React frontend
The React frontend is currently only available locally (not using Docker compose) while in development.

#### React Requirements
- NPM ([installation guide](https://nodejs.org/en/download/))
- NVM ([installation guide](https://github.com/nvm-sh/nvm#installing-and-updating))

#### Setup React project
1. Start Django server (see `django` alias creation below)
4. Open the frontend directory at `frontend`
5. Run `nvm use`
6. Install required packages with `npm install --legacy-peer-deps`
7. Generate the relay schema with `npm run relay`
8. Run tests to make sure everything is setup correctly with `npm test`.
9. Start the server with `npm run dev` and open http://localhost:X where X is the local address the output of the command gives you.
10. More tests can be run using `npm run cypress`.

### Creating other users
You likely want to create at least one Django user via that admin page although the superuser will be able to view the data as well. If you want to mimick the actual setup more closely, you can also setup a second user with permissions to create observations (`dataportal | observations | Can add observations`) and use that user for ingesting data.

### Daily local use
You can set up the following aliases in your `.bashrc` (`.zshrc` for Mac) to set up Django then React locally, replacing paths as required:
```
alias djangomanage="cd yourpath/meertime_dataportal/backend/ && poetry run python manage.py"
alias django="cd yourpath/meertime_dataportal/backend/ && poetry run python manage.py graphql_schema && poetry run python manage.py runserver"
alias react="cd yourpath/meertime_dataportal/frontend/ && npm run relay && npm run dev"
```

GraphQL queries can be made at http://localhost:8000/graphql/ or running a Django shell in the `backend` directory: `poetry run python manage.py shell_plus`.

## Alternative setup: to run the application using docker-compose

1. Clone the repository.
2. (optional but recommended) prepare environment and set it up with `set -a; source src/.env` where `src/.env` is based on `src/.env.template`. Note that if you're using .env file in docker-compose, you need to set `DB_HOST` to `mysql`
3. Run `docker-compose up`.

Currently, manual initialisation of the DB and migration are required. To do this, get a shell in the django container:
`docker exec -it $(docker container ls | grep meertime | grep django | awk '{print $1}') /bin/bash`. Then create users as detailed above in the local server instructions.

When building the images, we recommend running:
`DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose up --build`
for optimal image size and build speed.

### To use development mode in docker-compose

If you want to use DEVELOPMENT_MODE=True in docker-compose, the process is slightly different. First, you need to build the images:

`DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build --build-arg DEVELOPMENT_MODE=True`

followed by bringing the images up:

`docker-compose up`

## Contributing

Contributions can be made to the code base on GitLab.

### Testing

To manually run tests of the backend, execute `poetry run pytest` while in the `backend` directory.
To manually run tests of the frontend, run `npm run cypress` in the `frontend` directory.

### Adding requirements

Requirements are managed using [python poetry](https://python-poetry.org/).

#### Add a production package
1. Run `poetry add hello` to add package `hello`
2. Run `poetry install`
3. Update requirements.txt with `poetry export -f requirements.txt --without-hashes > src/requirements.txt`. We may move to using poetry in docker too but while we use alpine images, we will stick with this method.

#### Add a development package
1. Run `poetry add --dev hello` to add development package `hello`
2. Follow the steps for production package aside from the 1st step
3. Update requirements.dev.txt with `poetry export --dev -f requirements.txt --without-hashes > src/requirements.dev.txt`. We may move to using poetry in docker too but while we use alpine images, we will stick with this method.

## Uninstall
Local install:

From the `backend` folder: `poetry env list` then `poetry env remove` the relevant environment.
From the `frontend` folder, use `npm` to uninstall.