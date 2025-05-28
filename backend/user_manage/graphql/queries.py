"""
GraphQL queries for user management
"""

import graphene
from graphene import relay

from .decorators import login_required
from .token_mutations import ApiTokenConnection
from ..models import ApiToken


class Query(graphene.ObjectType):
    """User management queries"""

    # API Token connection for listing user's tokens
    api_tokens = relay.ConnectionField(
        ApiTokenConnection, description="List all API tokens for the authenticated user"
    )

    @login_required
    def resolve_api_tokens(self, info, **kwargs):
        """Resolve API tokens for the current user"""
        user = info.context.user
        return ApiToken.objects.filter(user=user).order_by("-created")
