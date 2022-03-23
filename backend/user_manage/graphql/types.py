import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from ..models import Registration


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
