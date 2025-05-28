"""
GraphQL mutations for Bearer token authentication
"""

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from django.db import IntegrityError
from graphql_relay import from_global_id

from ..models import ApiToken
from .decorators import login_required


class ApiTokenNode(DjangoObjectType):
    """Relay-compatible API token node"""

    class Meta:
        model = ApiToken
        fields = [
            "name",
            "preview",  # This will always show the first 8 characters
            "created",
            "last_used",
            "expires_at",
            "is_active",
        ]
        interfaces = (relay.Node,)

    # Explicitly define the preview field type since it's a model property, not a database field
    preview = graphene.String()


class ApiTokenConnection(relay.Connection):
    """Relay connection for API tokens"""

    class Meta:
        node = ApiTokenNode


class CreateApiTokenInput(graphene.InputObjectType):
    """Input for creating a new API token"""

    name = graphene.String(required=False, default_value="API Token")


class DeleteApiTokenInput(graphene.InputObjectType):
    """Input for deleting an API token"""

    token_id = graphene.ID(required=True)


class CreateApiToken(graphene.Mutation):
    """
    Create a new API token for the authenticated user
    """

    class Arguments:
        input = CreateApiTokenInput(required=True)

    # Return fields
    token = graphene.Field(ApiTokenNode)
    token_value = graphene.String()  # Return the full token value directly
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, input):
        user = info.context.user
        name = input.name or "API Token"

        try:
            # Create the token
            token = ApiToken.objects.create(user=user, name=name)

            return CreateApiToken(
                token=token,
                token_value=token.key,  # Return the full token value directly
                ok=True,
                errors=None,
            )
        except IntegrityError as e:
            # Handle unique constraint violation for token names
            error_msg = f"You already have a token named '{name}'. Please use a different name."

            return CreateApiToken(
                token=None,
                token_value=None,
                ok=False,
                errors=[error_msg],
            )


class DeleteApiToken(graphene.Mutation):
    """
    Delete an API token for the authenticated user
    """

    class Arguments:
        input = DeleteApiTokenInput(required=True)

    # Return fields
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, input):
        user = info.context.user

        try:
            # Decode the Relay Global ID to get the actual database ID
            try:
                node_type, token_id = from_global_id(input.token_id)
                if node_type != "ApiTokenNode":
                    return DeleteApiToken(
                        ok=False,
                        errors=["Invalid token ID"],
                    )
            except Exception:
                return DeleteApiToken(
                    ok=False,
                    errors=["Invalid token ID format"],
                )

            token = ApiToken.objects.get(id=token_id, user=user)
            token.delete()

            return DeleteApiToken(
                ok=True,
                errors=None,
            )

        except ApiToken.DoesNotExist:
            return DeleteApiToken(
                ok=False,
                errors=["Token not found or you don't have permission to delete it"],
            )

        except Exception as e:
            return DeleteApiToken(
                ok=False,
                errors=[str(e)],
            )


class TokenMutation(graphene.ObjectType):
    """
    Token-related GraphQL mutations
    """

    create_api_token = CreateApiToken.Field()
    delete_api_token = DeleteApiToken.Field()
