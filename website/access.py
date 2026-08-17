"""Restrict unpublished site sections (eSIM, insurance) to Django staff."""

from functools import wraps

from django.http import Http404


def is_staff_user(user) -> bool:
    return bool(user and user.is_authenticated and user.is_staff)


def staff_required(view_func):
    """Return 404 to anyone who is not a logged-in admin/staff user."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_staff_user(getattr(request, 'user', None)):
            raise Http404()
        return view_func(request, *args, **kwargs)

    return _wrapped
