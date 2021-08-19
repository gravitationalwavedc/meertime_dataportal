# Graphene graphql server settings
# https://docs.graphene-python.org/projects/django/en/latest/settings/

GRAPHENE = {
    "SCHEMA": "meertime.schema.schema",
    "SCHEMA_OUTPUT": "./frontend/data/schema.json",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware"],
}
