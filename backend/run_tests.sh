#!/bin/bash
export TESTING=True

poetry run python manage.py test "$@"
