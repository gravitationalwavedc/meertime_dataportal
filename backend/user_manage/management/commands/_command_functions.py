from time import sleep

from django.db import IntegrityError
from tqdm import tqdm

from utils.constants import UserRole
from user_manage.models import ProvisionalUser


def notify_provisional_users(filename=None, role=None):

    # Setting the role of the user(s)
    if role.casefold() == UserRole.ADMIN.value:
        role = UserRole.ADMIN.value
    elif role.casefold() == UserRole.UNRESTRICTED.value:
        role = UserRole.UNRESTRICTED.value
    else:
        role = UserRole.RESTRICTED.value

    if not filename:
        print('Please provide a filename to read from')

    # Read the file to get the email addresses
    print('Reading email addresses from the file')
    try:
        with open(filename, "r") as f:
            emails = f.readlines()
    except FileNotFoundError:
        print(f'File not found with name: {filename}')
    except Exception as ex:
        print(ex)

    # Create provisional user for those email addresses
    print('Creating provisional users...')
    for email in tqdm(emails):
        # get rid of the newline from the email address
        email = email.strip()

        try:
            provisional_user = ProvisionalUser(
                email=email,
                role=role,
            )
            provisional_user.save()
            provisional_user.refresh_from_db()

        except IntegrityError:
            print(f'Email address {email.strip()} already exists.')
        except Exception as ex:
            print(ex)
        else:
            print(f'Provisional user has been created for {email.strip()}')
            if provisional_user.email_sent:
                print(f'Activation email has been sent.')
                # wait for 1 second after a successful entry to allow sometime for the GPO to send out emails
                print('Waiting for 1 second to allow sometime for the GPO to send out emails...')
                sleep(1)
            else:
                print(f'Activation email was not sent :( .')
