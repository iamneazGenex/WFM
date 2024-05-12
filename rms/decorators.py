from django.http import Http404
from .constants import GroupEnum


def check_user_able_to_see_page(*groups: GroupEnum):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(
                name__in=[group.value for group in groups]
            ).exists():
                return function(request, *args, **kwargs)
            raise Http404

        return wrapper

    return decorator
