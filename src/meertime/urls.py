"""meertime URL Configuration
"""
import debug_toolbar

from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .schema import schema

handler500 = "dataportal.views.handler500"

urlpatterns = [
    path("meertime/", include("dataportal.urls")),
    path("MeerTime/", include("dataportal.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=settings.DEVELOPMENT_MODE))),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

if settings.DEVELOPMENT_MODE:
    urlpatterns.append(path("admin/", admin.site.urls))
