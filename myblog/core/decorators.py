from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse, HttpRequest

from typing import Callable, Any


def author_required(view_func: Callable) -> Any:

    @wraps(view_func)
    def _check_user_account(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user = request.user

        if not user.is_authenticated:
            messages.info(request, 'Please login to view this page.')
            return redirect_to_login(request.path_info)

        if not user.is_staff and not user.is_superuser:
            messages.info(request, "You can't access this page")
            return redirect_to_login(request.path_info)

        return view_func(request, *args, **kwargs)

    return _check_user_account