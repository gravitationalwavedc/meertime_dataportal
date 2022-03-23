import graphene

from uuid import UUID
from ..models import Registration
from .types import RegistrationInput, RegistrationType


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


class Mutation(graphene.ObjectType):
    create_registration = CreateRegistration.Field()
    verify_registration = VerifyRegistration.Field()
