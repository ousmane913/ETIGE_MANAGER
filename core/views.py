import json
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from inertia import render

logger = logging.getLogger(__name__)
from business.models import Client, Project, Quote, Site

def health_check(request):
    """Endpoint léger pour le health check Render — aucune dépendance frontend."""
    return JsonResponse({'status': 'ok'})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    # S'assurer que le super-utilisateur par défaut existe et a le bon mot de passe
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@etige.ci', 'admin')
        else:
            admin_user = User.objects.filter(username='admin').first()
            if admin_user:
                admin_user.set_password('admin')
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
    except Exception:
        pass

    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        # Lire les identifiants depuis request.POST (peuplé par JsonRequestMiddleware)
        # ou directement depuis le body JSON en fallback.
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not username and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                username = body.get('username', '')
                password = body.get('password', '')
            except (json.JSONDecodeError, Exception):
                pass

        logger.info('Login attempt — content_type=%s username=%r post_keys=%s',
                    request.content_type, username, list(request.POST.keys()))

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        logger.warning('Login failed for username=%r', username)
        return render(request, 'Auth/Login', {'error': 'Identifiants invalides.'})
    return render(request, 'Auth/Login')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'Dashboard', {
        'metrics': {'clients': Client.objects.count(), 'projects': Project.objects.count(), 'quotesPending': Quote.objects.filter(status=Quote.Status.DRAFT).count(), 'activeSites': Site.objects.filter(status=Site.Status.IN_PROGRESS).count()},
        'recentProjects': list(Project.objects.order_by('-created_at').values('id', 'name', 'status', 'client')[:6]),
        'user': {'name': request.user.get_full_name() or request.user.username, 'role': request.user.groups.first().name if request.user.groups.exists() else 'Administrateur'},
    })