from functools import wraps
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.auth.decorators import user_passes_test as django_user_passes_test
from django.contrib.auth.decorators import permission_required as django_permission_required
from graphql.error import GraphQLError


def login_required(f):
    @wraps(f)
    def wrapper(root, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in to perform this action")
        return f(root, info, **kwargs)

    return wrapper


def user_passes_test(test_func):
    """Decorator to determine if a user passes a test"""

    def decorator(f):
        @wraps(f)
        def wrapper(root, info, **kwargs):
            if not test_func(info.context.user):
                raise GraphQLError("You do not have permission to perform this action")
            return f(root, info, **kwargs)

        return wrapper

    return decorator


def permission_required(perm):
    """Decorator to check if a user has a specific permission"""

    def decorator(f):
        @wraps(f)
        def wrapper(root, info, **kwargs):
            if not info.context.user.has_perm(perm):
                raise GraphQLError(f"You don't have the required permission: {perm}")
            return f(root, info, **kwargs)

        return wrapper

    return decorator
