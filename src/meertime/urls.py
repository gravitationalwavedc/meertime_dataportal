"""meertime URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from .settings import DEBUG
from .schema import schema


urlpatterns = [
    path("meertime/", include("dataportal.urls")),
    path("MeerTime/", include("dataportal.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=DEBUG))),
]
