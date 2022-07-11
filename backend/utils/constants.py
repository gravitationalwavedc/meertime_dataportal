from enum import Enum
from django.utils.translation import gettext_lazy as _


class UserRole(Enum):
    RESTRICTED = 'RESTRICTED'  # restricted role can have no access to the embargoed data
    UNRESTRICTED = 'UNRESTRICTED'  # unrestricted should be able to view any data
    ADMIN = 'ADMIN'  # provisional, not used right now, has admin rights, ex: change user-roles via the front-end
