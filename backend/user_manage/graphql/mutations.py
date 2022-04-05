import django.contrib.auth
import graphene

from django.utils import timezone
from uuid import UUID
from django.db.models import Q

from ..models import (
    Registration,
    PasswordResetRequest,
)
from .types import (
    RegistrationInput,
    RegistrationType,
    PasswordResetRequestType,
)

UserModel = django.contrib.auth.get_user_model()


class CreateRegistration(graphene.Mutation):
    class Arguments:
        input = RegistrationInput(required=True)

    ok = graphene.Boolean()
    registration = graphene.Field(RegistrationType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, self, info, input):
        try:
            registration = Registration.objects.create(**input.__dict__)
            return CreateRegistration(
                ok=True,
                registration=registration,
                errors=None,
            )
        except Exception as exp:
            return CreateRegistration(
                ok=False,
                registration=None,
                errors=exp.messages,
            )


class VerifyRegistration(graphene.Mutation):
    class Arguments:
        verification_code = graphene.String(required=True)

    ok = graphene.Boolean()
    registration = graphene.Field(RegistrationType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, self, info, verification_code):
        try:
            UUID(str(verification_code), version=4)
        except ValueError:
            return VerifyRegistration(
                ok=False,
                registration=None,
                errors=['Invalid verification code.'],
            )

        try:
            registration = Registration.objects.get(verification_code=verification_code)
            if registration.status == Registration.VERIFIED:
                return VerifyRegistration(
                    ok=False,
                    registration=None,
                    errors=['Email already verified.'],
                )
            registration.status = Registration.VERIFIED
            registration.save()
            return VerifyRegistration(
                ok=True,
                registration=registration,
                errors=None,
            )
        except Registration.DoesNotExist:
            return VerifyRegistration(
                ok=False,
                registration=None,
                errors=['Verification code does not exist.'],
            )
        except Exception as exp:
            return VerifyRegistration(
                ok=False,
                registration=None,
                errors=exp.messages,
            )


class CreatePasswordResetRequest(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    ok = graphene.Boolean()
    password_reset_request = graphene.Field(PasswordResetRequestType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, self, info, email):
        try:
            password_reset_request = PasswordResetRequest.objects.create(email=email)
            return CreatePasswordResetRequest(
                ok=True,
                password_reset_request=password_reset_request,
                errors=None,
            )
        except Exception as exp:
            return CreatePasswordResetRequest(
                ok=False,
                password_reset_request=None,
                errors=exp.messages,
            )


class PasswordReset(graphene.Mutation):
    class Arguments:
        verification_code = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()
    password_reset_request = graphene.Field(PasswordResetRequestType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, self, info, verification_code, password):
        try:
            UUID(str(verification_code), version=4)
        except ValueError:
            return PasswordReset(
                ok=False,
                password_reset_request=None,
                errors=['Invalid verification code.'],
            )

        try:
            password_reset_request = PasswordResetRequest.objects.get(verification_code=verification_code)

            if password_reset_request.verification_expiry < timezone.now():
                return PasswordReset(
                    ok=False,
                    password_reset_request=None,
                    errors=['The verification code has been expired.'],
                )

            if password_reset_request.status == PasswordResetRequest.UPDATED:
                return PasswordReset(
                    ok=False,
                    password_reset_request=None,
                    errors=['The verification code has been used.'],
                )

            # change the user password here
            # get the user whose password will be changed
            user = UserModel.objects.filter(
                Q(username=password_reset_request.email) |
                Q(email=password_reset_request.email)
            ).first()

            if user:
                user.set_password(raw_password=password)
                user.save()

                # update the request so that same verification code cannot be used again
                password_reset_request.status = PasswordResetRequest.UPDATED
                password_reset_request.save()
                return PasswordReset(
                    ok=True,
                    password_reset_request=password_reset_request,
                    errors=None,
                )
            else:
                # this will only be fired if a user gets deleted after the password reset verification code is sent
                return PasswordReset(
                    ok=False,
                    password_reset_request=None,
                    errors=['No user found. Please contact support regarding this.'],
                )
        except PasswordResetRequest.DoesNotExist:
            return PasswordReset(
                ok=False,
                password_reset_request=None,
                errors=['Verification code does not exist.'],
            )
        except Exception as exp:
            return PasswordReset(
                ok=False,
                registration=None,
                errors=exp.messages,
            )


class Mutation(graphene.ObjectType):
    create_registration = CreateRegistration.Field()
    verify_registration = VerifyRegistration.Field()
    create_password_reset_request = CreatePasswordResetRequest.Field()
    password_reset = PasswordReset.Field()
