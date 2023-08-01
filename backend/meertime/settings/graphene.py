# Graphene graphql server settings
# https://docs.graphene-python.org/projects/django/en/latest/settings/

GRAPHENE = {
    "SCHEMA": "meertime.schema.schema",
    "SCHEMA_OUTPUT": "../frontend/src/schema.graphql",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware"],
}
