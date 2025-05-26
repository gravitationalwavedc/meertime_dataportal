#!/bin/bash
COVERAGE_PROCESS_START=./.coveragerc poetry run coverage run --rcfile=./.coveragerc manage.py test --parallel $(($(nproc) * 2)) $@ &&
  poetry run coverage combine --rcfile=./.coveragerc &&
  poetry run coverage xml --rcfile=./.coveragerc -o coverage.xml &&
  poetry run coverage report --rcfile=./.coveragerc
