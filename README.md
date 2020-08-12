# MeerTime

## About
The MeerTime project is a five-year program on the MeerKAT array by an international consortium that will regularly time over 1000 radio pulsars to perform tests of relativistic gravity, search for the gravitational wave signature induced by supermassive black hole binaries in the timing residuals of millisecond pulsars, explore the interiors of neutron stars through a pulsar glitch monitoring programme, explore the origin and evolution of binary pulsars, monitor the swarms of pulsars that inhabit globular clusters and monitor radio magnetars. MeerTime will complement the TRAPUM project and time pulsars TRAPUM discovers in surveys of the galactic plane, globular clusters and the galactic centre. In addition to these primary programmes, over 1000 pulsars will have their arrival times monitored and the data made immediately public.

This application provides a ReactJS frontend for access to the MeerTime project data for authenticated astronomers and provides a Django powered graphql API.


## Requirements
* Python >= 3.8
* Python VirtualEnv

### To run on your local machine
* MySQL server 

### To run in Docker
* Docker
* Docker Compose

## Setup
### To run on your local machine

1. Clone the repository.
2. Install python packges using [python poetry](https://python-poetry.org/):
Run `poetry install --no-dev` for minimum install. This only installs required production packages.  
Run `poetry install` to also install development packages such as testing tools.

3. `cd src`
4. Start the development server.
  Run `poetry run python manage.py runserver` and open the [development server](http://localhost:8000/meertime).

(Optional):

5. Insert some data into the DB by running `poetry run python ingest/ingest.py`

### To run the application using docker-compose

1. Clone the repository.
2. Run `docker-compose up`.

Currently, manual initialisation of the DB and migration are required.

## Contributing

Contributions can be made to the code base on Phabricator via arcanist. All diffs should include sosl as a reviewer.

### Testing

To manually run tests, execute `poetry run pytest` (or simply `pytest` if running in a shell spawned by `poetry shell`) while in the `src` directory. 

### Arcanist workflow

1. On master branch run `arc work {branch-name}` with your chosen branch name.
2. Keep track of code changes with `git add .` and `git commit`.
3. When you're ready to push your changes for review run `arc diff` in your working branch.
4. Once your diff has been reviewed and accepted run `arc land` in your working branch. This will close the branch and push to master.

### Adding requirements

Requirements are managed using [python poetry](https://python-poetry.org/).

#### Add a production package
1. Run `poetry add hello` to add package `hello`
2. Run `poetry install`
3. Update requirements.txt with `poetry export -f requirements.txt --without-hashes > src/requirements.txt`. We may move to using poetry in docker too but while we use alpine images, we will stick with this method.

#### Add a development package
1. Run `poetry add --dev hello` to add development package `hello`
2. Follow the steps for production package aside from the 1st step

#### Installing black linter for use with arcanist:
1. Go to the top directory of where you have install arcanist `cd arcanist_top_dir`
2. `git clone https://github.com/pinterest/arcanist-linters.git pinterest-linters`
3. Go to your repo `cd repo_dir`
4. `ln -s arcanist_top_dir/pinterest-linters .pinterest-linters`

