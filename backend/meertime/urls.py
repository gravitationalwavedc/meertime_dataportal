"""meertime URL Configuration
"""
from django.contrib import admin
from django.urls import include, path, re_path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from utils.utility import secure_serve

from .schema import schema

handler500 = "dataportal.views.handler500"

urlpatterns = [
    path("", include("dataportal.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    re_path(r'^media/(?P<path>.*)$', secure_serve, {'document_root': settings.MEDIA_ROOT}),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=settings.DEVELOPMENT_MODE))),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    # debug_toolbar not available in production environment
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

if settings.DEVELOPMENT_MODE:
    urlpatterns.append(path("admin/", admin.site.urls))
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
