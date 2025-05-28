from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from graphene_django.views import GraphQLView
from django.conf import settings
from django.contrib.auth import authenticate
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class GraphQLAuthenticationMiddleware:
    """
    Middleware to handle both session and Bearer token authentication for GraphQL requests.
    This middleware ensures that GraphQL requests properly utilize Django's authentication
    and that user information is available in the GraphQL context.

    Supports both session-based authentication (for web browsers) and Bearer token
    authentication (for API clients) in a single, unified middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process Bearer token authentication for all requests
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            user = authenticate(request, token=token)
            if user and user.is_authenticated:
                request.user = user
                # Skip CSRF for Bearer token requests
                request._dont_enforce_csrf_checks = True
                if settings.DEBUG:
                    logger.debug(f"Bearer token authentication successful for user: {user.username}")

        # Process the request
        if self._is_graphql_request(request):
            self._prepare_graphql_context(request)

        # Get response from next middleware/view
        response = self.get_response(request)

        # Process the response if needed
        if self._is_graphql_request(request):
            # Add any headers or modify response for GraphQL requests if needed
            # For example, you might want to add CORS headers specifically for GraphQL
            pass

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This method is called just before Django calls the view
        # If this is a GraphQL view, ensure authentication context is properly set
        if isinstance(getattr(view_func, "view_class", None), GraphQLView):
            # Store any additional context needed for GraphQL resolvers
            request.graphql_context = {
                "is_authenticated": request.user.is_authenticated,
                "user_id": request.user.id if request.user.is_authenticated else None,
                "user_role": (getattr(request.user, "role", None) if request.user.is_authenticated else None),
            }

            # Log auth status for debugging
            if settings.DEBUG:
                auth_header = request.META.get("HTTP_AUTHORIZATION", "")
                auth_method = "Bearer token" if auth_header.startswith("Bearer ") else "Session"
                logger.debug(
                    f"GraphQL request ({auth_method}) from user: {request.user.username if request.user.is_authenticated else 'Anonymous'}"
                )

        return None

    def _is_graphql_request(self, request):
        """Check if the current request is a GraphQL request"""
        graphql_url = reverse("graphql")
        return request.path == graphql_url

    def _prepare_graphql_context(self, request):
        """Prepare the request object for GraphQL by ensuring user info is available"""
        # User is already set by AuthenticationMiddleware, but we can add extra context
        # or handle specific GraphQL authentication requirements

        # Ensure CSRF is properly checked for mutation operations (POST requests)
        # Skip CSRF for Bearer token requests as they don't use cookies
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if request.method == "POST" and not getattr(request, "_dont_enforce_csrf_checks", False):
            # Skip CSRF for Bearer token requests
            if auth_header.startswith("Bearer "):
                request._dont_enforce_csrf_checks = True
            # Django's CSRF middleware should handle session-based requests

        # Add session expiry check if needed
        if request.user.is_authenticated and hasattr(request, "session"):
            # Check if session is about to expire and might need renewal
            if "session_expires_at" in request.session:
                # You could implement session extension logic here
                pass
