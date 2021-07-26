MeerTime
=============
The MeerTime project is a five-year program on the MeerKAT array by an international consortium that will regularly time over 1000 radio pulsars to perform tests of relativistic gravity, search for the gravitational wave signature induced by supermassive black hole binaries in the timing residuals of millisecond pulsars, explore the interiors of neutron stars through a pulsar glitch monitoring programme, explore the origin and evolution of binary pulsars, monitor the swarms of pulsars that inhabit globular clusters and monitor radio magnetars. MeerTime will complement the TRAPUM project and time pulsars TRAPUM discovers in surveys of the galactic plane, globular clusters and the galactic centre. In addition to these primary programmes, over 1000 pulsars will have their arrival times monitored and the data made immediately public.

This application provides a ReactJS frontend for access to the MeerTime project data for authenticated astronomers and provides a Django powered graphql API.

Requirements
============

* Python >= 3.8
* Python VirtualEnv
  
## To run on your local machine
* MySQL server 

## To run in Docker
* Docker
* Docker Compose

## Building docker images
* We recommend setting DOCKER_BUILDKIT=1 before building images for optimal build time and final image size

Setup
=====

## To run on your local machine

* Clone the repository.
* Install python packges using [python poetry](https://python-poetry.org/):
Run `poetry install --no-dev` for minimum install. This only installs required production packages.  
Run `poetry install` to also install development packages such as testing tools.

* `cd src`
* Start the development server.
  Run `poetry run python manage.py runserver` and open the [development server](http://localhost:8000/meertime).

(Optional):

* Insert some data into the DB by running `poetry run python ingest/ingest.py`

## To run the application using docker-compose

* Clone the repository.
* (optional but recommended) prepare environment and set it up with `set -a; source src/.env` where `src/.env` is based on `src/.env.template`. Note that if you're using .env file in docker-compose, you need to set `DB_HOST` to `mysql`
* Run `docker-compose up`.


When building the images, we recommmend running:
`DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose up --build`
for optimal image size and build speed.

Currently, manual initialisation of the DB and migration are required. To do this, get a shell in the django container:

`docker exec -it $(docker container ls | grep meertime | grep django | awk '{print $1}') /bin/bash`

and execute the following:

`python manage.py migrate`

`python manage.py createsuperuser`

You likely want to create at least one user via the admin page (available at http://localhost:8000/admin) although the admin user will be able to view the data as well. If you want to mimick the actual setup more closely, you can also setup a second user with permissions to create observations (`dataportal | observations | Can add observations`) and use that user for ingesting data. 


### To use development mode in docker-compose

If you want to use DEVELOPMENT_MODE=True in docker-compose, the process is slightly different. First, you need to build the images:

`DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build --build-arg DEVELOPMENT_MODE=True`

followed by bringing the images up:

`docker-compose up`


## To deploy on a kubernetes cluster

The whole app is designed to work in a kubernetes cluster, in particular to use the GWDC operated cluster. If desired (e.g, for local deployment for testing purposes), the k8s cluster can be easily recreated from this repository:https://github.com/gravitationalwavedc/gwc_devops

Prerequisities (fulfiled by the linked k8s cluster):
1. A hashicorp vault (for storing secrets and configuration)
2. A sonata nexus or another repository to serve as a docker register and a raw file storage (for sql initialisation files)
3. (Optional) Argo CD to facilitate deployment and sync with the repository

### Vault configuration

The vault needs to be configured with appropriate ACL policies and roles to allow the app to read secrets but configuring this is beyond this scope of this readme. Please refer to hashicorp vault documentation. 

Note that all values need to be stored as base64 encoded strings. The following secrets need to exist in the key-value store at meertime/kv path:
1. db-config
    1. MYSQL_DATABASE - defines the name of the DB to be used by the app
    2. MYSQL_PASSWORD - define the password for the DB
    3. MYSQL_UESR - define the user for the DB
2. db-control
    1. FORCE_RELOAD - controls if the database needs to be re-initialised using a script stored on nexus. Set to "FORCE_RELOAD" to do so
3. dbroot
    1. password - define root password for the MYSQL DB
4. django-multi
    1. DJANGO_SECRET_KEY - define the django variable with the same name
    2. ENV - define a environment variable with the same name. Used to ensure django running k8s is configured from vault rather than .env file
    3. KRONOS_PAYLOAD - payload for easier transition between pages
    4. SENTRY_DSN - DSN for sentry.io (note: appears to be broken as of April 2021)
    5. SLACK_WEBHOOK - webhook for notifications on slack when new data is added to the DB
5. nexus/service
    1. NEXUS_CONTROL_DIR - directory on raw file repository with mysql initialisation scripts
    2. NEXUS_PASS - nexus password
    3. NEXUS_URL - nexus URL
    4. NEXUS_USER - nexus username

Furthermore, the vault needs to store docker registry credentials at the nexus/kv/docker path

## Deployment

We use Argo CD for deployment. Any new kubernetes manifests need to be added to kubernetes/manifests directory. Do not forget to add the manifest to kustomization.yaml as well.

Starting the React Frontend
===========================
The react frontend is currently only available locally while in developement.

## React Requirements
- NPM ([installation guide](https://nodejs.org/en/download/))
- NVM ([installation guide](https://github.com/nvm-sh/nvm#installing-and-updating))

## Setup React project
1. Open the django project at meertime-data-portal/src
2. Generate the relay schema by running `poetry run python manage.py graphql_schema`
3. Start the django development server and make sure it's running on http://localhost:8000
4. Open the frontend directory at meertime-data-portal/src/frontend
5. Run `nvm use`
6. Install required packages with `npm install`
7. Generate the relay schema with `npm run relay`
8. Run tests to make sure everything is setup correctly with `npm test`
9. Start the server with `npm start`
10. Open https://localhost:3000

## Starting React after setup is complete
1. Generate the relay schema with `npm run relay`
2. Run tests to make sure everything is setup correctly with `npm test`
3. Start the server with `npm start`
4. Open https://localhost:3000

Contributing
============
Contributions can be made to the code base on Phabricator via arcanist. All diffs should include sosl as a reviewer.

Testing
============
To manually run tests, execute `poetry run pytest` (or simply `pytest` if running in a shell spawned by `poetry shell`) while in the `src` directory. 

Arcanist workflow
=================
1. On master branch run `arc work {branch-name}` with your chosen branch name.
2. Keep track of code changes with `git add .` and `git commit`.
3. When you're ready to push your changes for review run `arc diff` in your working branch.
4. Once your diff has been reviewed and accepted run `arc land` in your working branch. This will close the branch and push to master.

Adding requirements
===================
Requirements are managed using [python poetry](https://python-poetry.org/).

## Add a production package
1. Run `poetry add hello` to add package `hello`
2. Run `poetry install`
3. Update requirements.txt with `poetry export -f requirements.txt --without-hashes > src/requirements.txt`. We may move to using poetry in docker too but while we use alpine images, we will stick with this method.

## Add a development package
1. Run `poetry add --dev hello` to add development package `hello`
2. Follow the steps for production package aside from the 1st step
3. Update requirements.dev.txt with `poetry export --dev -f requirements.txt --without-hashes > src/requirements.dev.txt`. We may move to using poetry in docker too but while we use alpine images, we will stick with this method.

## Installing black linter for use with arcanist:
1. Go to the top directory of where you have install arcanist `cd arcanist_top_dir`
2. `git clone https://github.com/pinterest/arcanist-linters.git pinterest-linters`
3. Go to your repo `cd repo_dir`
4. `ln -s arcanist_top_dir/pinterest-linters .pinterest-linters`

