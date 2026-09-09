from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

ROLE_EMPLOYEE = 'Employé'
ROLE_MANAGER = 'Manager'
ROLE_DT = 'DT'
ROLE_DG = 'DG'

ROLES = (ROLE_EMPLOYEE, ROLE_MANAGER, ROLE_DT, ROLE_DG)

MSG_DG_ONLY_EDIT = 'Seul le Directeur Général (DG) dispose des autorisations pour modifier le projet.'
MSG_DG_ONLY_DELETE_PROJECT = 'Seul le Directeur Général (DG) est habilité à supprimer un projet.'
MSG_DG_ONLY_DELETE_CLIENT = 'Seul le Directeur Général (DG) est habilité à supprimer un client.'


def _in_group(user, *names):
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.groups.filter(name__in=names).exists()


def is_dg(user):
    return bool(getattr(user, 'is_superuser', False) or _in_group(user, ROLE_DG))


def is_dt(user):
    return _in_group(user, ROLE_DT)


def can_view_financials(user):
    return is_dg(user) or is_dt(user)


def can_edit_project(user):
    return is_dg(user)


def can_delete_project(user):
    return is_dg(user)


def can_delete_client(user):
    return is_dg(user)


def role_flags(user):
    return {
        'isDg': is_dg(user),
        'isDt': is_dt(user),
        'isManagement': can_view_financials(user),
    }


def require_permission(check, message, fallback='projects'):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not check(request.user):
                messages.error(request, message)
                if 'project_id' in kwargs:
                    return redirect('project-detail', kwargs['project_id'])
                return redirect(fallback)
            return view(request, *args, **kwargs)
        return wrapped
    return decorator
