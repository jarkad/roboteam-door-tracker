from functools import wraps
from django.http import JsonResponse


def require_authentication(view_func):
    """
    Decorator to ensure the user is authenticated.
    If not, returns a JsonResponse error.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'status': 'error', 'message': 'Log in to continue.'},
                status=400,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped_view
