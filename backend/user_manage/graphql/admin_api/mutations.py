import graphene
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from graphql_jwt.decorators import user_passes_test

from user_manage.models import (
    ProvisionalUser,
    Registration,
)

from utils.constants import UserRole


User = get_user_model()


def set_role(role):
    # Setting the role of the user(s)
    if role.casefold() == UserRole.ADMIN.value.casefold():
        user_role = UserRole.ADMIN.value
    elif role.casefold() == UserRole.UNRESTRICTED.value.casefold():
        user_role = UserRole.UNRESTRICTED.value
    else:
        user_role = UserRole.RESTRICTED.value

    return user_role


class ActivateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    @user_passes_test(lambda user: user.role == UserRole.ADMIN.value)
    def mutate(cls, self, info, username):

        try:
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()
        except User.DoesNotExist:
            return ActivateUser(ok=False, errors=[f"User with username {username} does not exist."])
        except Exception as ex:
            return ActivateUser(
                ok=False,
                errors=ex.messages,
            )
        else:
            return ActivateUser(
                ok=True,
                errors=None,
            )


class DeactivateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    @user_passes_test(lambda user: user.role == UserRole.ADMIN.value)
    def mutate(cls, self, info, username):

        try:
            user = User.objects.get(username=username)
            user.is_active = False
            user.save()
        except User.DoesNotExist:
            return DeactivateUser(ok=False, errors=[f"User with username {username} does not exist."])
        except Exception as ex:
            return DeactivateUser(
                ok=False,
                errors=ex.messages,
            )
        else:
            return DeactivateUser(
                ok=True,
                errors=None,
            )


class DeleteUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    @user_passes_test(lambda user: user.role == UserRole.ADMIN.value)
    def mutate(cls, self, info, username):

        try:
            User.objects.filter(username=username).delete()
        except Exception as ex:
            return DeleteUser(
                ok=False,
                errors=ex.messages,
            )
        else:
            return DeleteUser(
                ok=True,
                errors=None,
            )


class CreateProvisionalUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        role = graphene.String(required=True)

    ok = graphene.Boolean()
    email_sent = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    @user_passes_test(lambda user: user.role == UserRole.ADMIN.value)
    def mutate(cls, self, info, email, role):
        try:
            provisional_user = ProvisionalUser.objects.create(
                email=email,
                role=set_role(role),
            )
        except IntegrityError:
            return CreateProvisionalUser(
                ok=False,
                email_sent=False,
                errors=[f"Email address {email} already exists."],
            )
        except Exception as ex:
            return CreateProvisionalUser(
                ok=False,
                email_sent=False,
                errors=ex.messages,
            )
        else:
            return CreateProvisionalUser(
                ok=True,
                email_sent=provisional_user.email_sent,
                errors=None,
            )


class UpdateRole(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        role = graphene.String()

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    @user_passes_test(lambda user: user.role == UserRole.ADMIN.value)
    def mutate(cls, self, info, username, role):
        try:
            user = User.objects.get(username=username)
            user.role = set_role(role)
            user.save()
        except User.DoesNotExist:
            return UpdateRole(ok=False, errors=[f"User with username {username} does not exist."])
        except Exception as ex:
            return UpdateRole(
                ok=False,
                errors=ex.messages,
            )
        else:
            return UpdateRole(
                ok=True,
                errors=None,
            )


class Mutation(graphene.ObjectType):
    create_provisional_user = CreateProvisionalUser.Field()
    delete_user = DeleteUser.Field()
    activate_user = ActivateUser.Field()
    deactivate_user = DeactivateUser.Field()
    update_role = UpdateRole.Field()
