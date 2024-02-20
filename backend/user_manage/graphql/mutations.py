import datetime
from uuid import UUID

import django.contrib.auth
import graphene
import requests
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from ..models import PasswordResetRequest, ProvisionalUser, Registration
from . import admin_api
from .types import PasswordResetRequestType, ProvisionalUserType, RegistrationInput, RegistrationType, UserType

UserModel = django.contrib.auth.get_user_model()


class CreateRegistration(graphene.Mutation):
    class Arguments:
        input = RegistrationInput(required=True)

    ok = graphene.Boolean()
    registration = graphene.Field(RegistrationType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, self, info, input):
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": settings.SECRET_CAPTCHA_KEY, "response": input.get("captcha")},
        )

        if not r.json()["success"]:
            return CreateRegistration(ok=False, registration=None, errors=["Captcha validation failed."])

        del input["captcha"]

        try:
            registration = Registration.objects.create(**input)
            return CreateRegistration(ok=True, registration=registration, errors=None)
        except Exception as e:
            return CreateRegistration(ok=False, registration=None, errors=e.messages)


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
            return VerifyRegistration(ok=False, registration=None, errors=["Invalid verification code."])

        try:
            registration = Registration.objects.get(verification_code=verification_code)
            if registration.status == Registration.VERIFIED:
                return VerifyRegistration(ok=False, registration=None, errors=["Email already verified."])
            registration.status = Registration.VERIFIED
            registration.save()
            return VerifyRegistration(ok=True, registration=registration, errors=None)
        except Registration.DoesNotExist:
            return VerifyRegistration(ok=False, registration=None, errors=["Verification code does not exist."])
        except Exception as e:
            return VerifyRegistration(ok=False, registration=None, errors=e.messages)


class AccountActivation(graphene.Mutation):
    class Arguments:
        user_input = RegistrationInput(required=True)
        activation_code = graphene.String(required=True)

    ok = graphene.Boolean()
    provisional_user = graphene.Field(ProvisionalUserType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, self, info, activation_code, user_input):
        try:
            UUID(str(activation_code), version=4)
        except ValueError:
            return AccountActivation(ok=False, provisional_user=None, errors=["Invalid verification code."])

        try:
            provisional_user = ProvisionalUser.objects.get(
                activation_code=activation_code, email=user_input.get("email")
            )
            if provisional_user.activated:
                return AccountActivation(ok=False, provisional_user=None, errors=["Account already activated."])

            provisional_user.user.set_password(user_input.get("password"))
            provisional_user.user.first_name = user_input.get("first_name")
            provisional_user.user.last_name = user_input.get("last_name")
            provisional_user.user.is_active = True
            provisional_user.user.save()

            provisional_user.activated = True
            provisional_user.activated_on = datetime.datetime.now()
            provisional_user.save()

            return AccountActivation(ok=True, provisional_user=provisional_user, errors=None)
        except ProvisionalUser.DoesNotExist:
            return AccountActivation(
                ok=False, provisional_user=None, errors=["Activation code for this email does not exist."]
            )
        except Exception as e:
            return AccountActivation(ok=False, provisional_user=None, errors=e.messages)


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
            return CreatePasswordResetRequest(ok=True, password_reset_request=password_reset_request, errors=None)
        except Exception as e:
            return CreatePasswordResetRequest(ok=False, password_reset_request=None, errors=e.messages)


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
            return PasswordReset(ok=False, password_reset_request=None, errors=["Invalid verification code."])

        try:
            password_reset_request = PasswordResetRequest.objects.get(verification_code=verification_code)

            if password_reset_request.verification_expiry < timezone.now():
                return PasswordReset(
                    ok=False, password_reset_request=None, errors=["The verification code has been expired."]
                )

            if password_reset_request.status == PasswordResetRequest.UPDATED:
                return PasswordReset(
                    ok=False, password_reset_request=None, errors=["The verification code has been used."]
                )

            # Change the user password here
            # Get the user whose password will be changed
            user = UserModel.objects.filter(
                Q(username=password_reset_request.email) | Q(email=password_reset_request.email)
            ).first()

            if user:
                user.set_password(raw_password=password)
                user.save()

                # update the request so that same verification code cannot be used again
                password_reset_request.status = PasswordResetRequest.UPDATED
                password_reset_request.save()
                return PasswordReset(ok=True, password_reset_request=password_reset_request, errors=None)
            else:
                # this will only be fired if a user gets deleted after the password reset verification code is sent
                return PasswordReset(
                    ok=False,
                    password_reset_request=None,
                    errors=["No user found. Please contact support regarding this."],
                )
        except PasswordResetRequest.DoesNotExist:
            return PasswordReset(ok=False, password_reset_request=None, errors=["Verification code does not exist."])
        except Exception as e:
            return PasswordReset(ok=False, registration=None, errors=e.messages)


class PasswordChange(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        old_password = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, self, info, username, old_password, password):
        try:
            if old_password == password:
                return PasswordChange(ok=False, user=None, errors=["New and current passwords cannot be same."])

            user = UserModel.objects.get(username=username)

            if user.check_password(old_password):
                user.set_password(password)
                user.save()
            else:
                return PasswordChange(ok=False, user=None, errors=["Current password is incorrect."])

            return PasswordChange(ok=True, user=user, errors=None)
        except UserModel.DoesNotExist:
            return PasswordChange(ok=False, user=None, errors=["User does not exist."])
        except Exception as e:
            return PasswordChange(ok=False, user=None, errors=e.messages)


class Mutation(admin_api.Mutation, graphene.ObjectType):
    create_registration = CreateRegistration.Field()
    verify_registration = VerifyRegistration.Field()
    create_password_reset_request = CreatePasswordResetRequest.Field()
    password_reset = PasswordReset.Field()
    password_change = PasswordChange.Field()
    account_activation = AccountActivation.Field()
