"""meertime URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from .settings import DEBUG, ADMIN_ENABLED, INSTALLED_APPS
from .schema import schema

handler500 = "dataportal.views.handler500"

urlpatterns = [
    path("meertime/", include("dataportal.urls")),
    path("MeerTime/", include("dataportal.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=DEBUG))),
]

if DEBUG and "debug_toolbar" in INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [
        path(r"^__debug__/", include(debug_toolbar.urls)),
    ]

if ADMIN_ENABLED:
    urlpatterns.append(path("admin/", admin.site.urls))
