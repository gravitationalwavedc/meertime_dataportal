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
2. Install python packges using [python poetry][https://python-poetry.org/]:
Run `poetry install --no-dev` for minimum install. This only installs required production packages.  
Run `poetry install` to also install development packages such as testing tools.

3. Start the development server.
  Run `poetry run python manage.py runserver` and open the [development server](http://localhost:8000/meertime).

### To run the application using docker-compose

1. Clone the repository.
2. Start docker-compose.

## Contributing

Contributions can be made to the code base on Phabricator via arcanist. All diffs should include sosl as a reviewer.

### Arcanist workflow

1. On master branch run `arc work {branch-name}` with your chosen branch name.
2. Keep track of code changes with `git add .` and `git commit`.
3. When you're ready to push your changes for review run `arc diff` in your working branch.
4. Once your diff has been reviewed and accepted run `arc land` in your working branch. This will close the branch and push to master.

### Adding requirements

Requirements are managed using [pip-tools](https://github.com/jazzband/pip-tools).

#### Add a production package
1. Add the required package to requirements.in
2. Run `pip-compile`
3. Run `pip-sync`

#### Add a development package
1. Add the required package to dev-requirements.in
2. Run `pip-compile dev-requirements.in`.
3. Run `pip-sync requirements.txt dev-requirements.txt`

