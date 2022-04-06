import graphene
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django import DjangoObjectType

from ..models import (
    Registration,
    PasswordResetRequest,
)


class RegistrationType(DjangoObjectType):
    class Meta:
        model = Registration
        interfaces = (relay.Node,)
        exclude = ['user', 'verification_code', 'password']


class RegistrationInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)


class PasswordResetRequestType(DjangoObjectType):
    class Meta:
        model = PasswordResetRequest
        interfaces = (relay.Node,)
        exclude = ['verification_code']


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (relay.Node,)
        exclude = ['password']
