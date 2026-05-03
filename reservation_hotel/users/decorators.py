from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def staff_required(view_func):
    """Decorator: user must be authenticated staff"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('staff_id'):
            messages.error(request, "Veuillez vous connecter.")
            return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """Decorator: user must have one of the specified roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get('staff_id'):
                messages.error(request, "Veuillez vous connecter.")
                return redirect('users:login')
            if request.current_user.role not in roles:
                messages.error(request, "Vous n'avez pas les permissions nécessaires.")
                return redirect('users:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def client_required(view_func):
    """Decorator: client must be authenticated"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('client_id'):
            messages.error(request, "Veuillez vous connecter.")
            return redirect('client:login')
        return view_func(request, *args, **kwargs)
    return wrapper
