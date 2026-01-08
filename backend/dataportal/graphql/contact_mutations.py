import graphene
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from dataportal.emails import send_contact_form_email


class ContactFormInput(graphene.InputObjectType):
    contact_type = graphene.String(required=True)
    message = graphene.String(required=True)
    link = graphene.String(required=False)
    email = graphene.String(required=False)
    name = graphene.String(required=False)
    captcha = graphene.String(required=True)


class SubmitContactForm(graphene.Mutation):
    class Arguments:
        input = ContactFormInput(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(root, info, input):
        # Verify captcha
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.SECRET_CAPTCHA_KEY,
                "response": input.get("captcha"),
            },
        )

        if not r.json()["success"]:
            return SubmitContactForm(ok=False, errors=["Captcha validation failed."])

        # Remove captcha from input
        del input["captcha"]

        # Get contact type and message
        contact_type = input.get("contact_type")
        message = input.get("message")
        link = input.get("link")

        # Validate message
        if not message or len(message.strip()) == 0:
            return SubmitContactForm(ok=False, errors=["Message is required."])

        if len(message) > 2000:
            return SubmitContactForm(ok=False, errors=["Message must be at most 2000 characters long."])

        # Validate contact type
        if contact_type not in ["Contact Us", "Report Issue"]:
            return SubmitContactForm(ok=False, errors=["Invalid contact type."])

        # If Report Issue, link is required
        if contact_type == "Report Issue":
            if not link or len(link.strip()) == 0:
                return SubmitContactForm(ok=False, errors=["Link is required when reporting an issue."])

        # Get user information
        user = info.context.user
        if user and user.is_authenticated:
            # Use authenticated user's information
            user_email = user.email
            user_name = user.get_full_name() or user.username
        else:
            # For unauthenticated users, require email and name
            user_email = input.get("email")
            user_name = input.get("name")

            if not user_email or len(user_email.strip()) == 0:
                return SubmitContactForm(ok=False, errors=["Email is required."])

            if not user_name or len(user_name.strip()) == 0:
                return SubmitContactForm(ok=False, errors=["Name is required."])

            # Validate email format using Django's built-in validator
            try:
                validate_email(user_email)
            except ValidationError:
                return SubmitContactForm(ok=False, errors=["Invalid email format."])

        # Send email to admin
        send_contact_form_email(
            contact_type=contact_type,
            message=message,
            user_email=user_email,
            user_name=user_name,
            link=link,
        )

        return SubmitContactForm(ok=True, errors=[])


class Mutation(graphene.ObjectType):
    submit_contact_form = SubmitContactForm.Field()
