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
    from datetime import date
    from dateutil.relativedelta import relativedelta
    from collections import defaultdict

    today = date.today()
    two_years_ago = today - relativedelta(years=2)

    projects = Project.objects.filter(created_at__date__gte=two_years_ago).values('created_at', 'status')

    # --- Mensuel : 12 derniers mois ---
    monthly = defaultdict(lambda: {'created': 0, 'closed': 0})
    for i in range(11, -1, -1):
        d = today - relativedelta(months=i)
        key = d.strftime('%b %Y')
        monthly[key]  # init

    for p in projects:
        d = p['created_at'].date()
        if d >= today - relativedelta(months=12):
            key = d.strftime('%b %Y')
            monthly[key]['created'] += 1
            if p['status'] == Project.Status.CLOSED:
                monthly[key]['closed'] += 1

    monthly_data = [{'label': k, 'created': v['created'], 'closed': v['closed']} for k, v in monthly.items()]

    # --- Trimestriel : 8 derniers trimestres ---
    def quarter_key(d):
        q = (d.month - 1) // 3 + 1
        return f'T{q} {d.year}'

    quarterly = defaultdict(lambda: {'created': 0, 'closed': 0})
    for i in range(7, -1, -1):
        d = today - relativedelta(months=i * 3)
        key = quarter_key(d)
        quarterly[key]  # init

    for p in projects:
        d = p['created_at'].date()
        if d >= today - relativedelta(months=24):
            key = quarter_key(d)
            if key in quarterly:
                quarterly[key]['created'] += 1
                if p['status'] == Project.Status.CLOSED:
                    quarterly[key]['closed'] += 1

    quarterly_data = [{'label': k, 'created': v['created'], 'closed': v['closed']} for k, v in quarterly.items()]

    # --- Semestriel : 4 derniers semestres ---
    def semester_key(d):
        s = 1 if d.month <= 6 else 2
        return f'S{s} {d.year}'

    semesterly = defaultdict(lambda: {'created': 0, 'closed': 0})
    for i in range(3, -1, -1):
        d = today - relativedelta(months=i * 6)
        key = semester_key(d)
        semesterly[key]  # init

    for p in projects:
        d = p['created_at'].date()
        if d >= today - relativedelta(months=24):
            key = semester_key(d)
            if key in semesterly:
                semesterly[key]['created'] += 1
                if p['status'] == Project.Status.CLOSED:
                    semesterly[key]['closed'] += 1

    semesterly_data = [{'label': k, 'created': v['created'], 'closed': v['closed']} for k, v in semesterly.items()]

    return render(request, 'Dashboard', {
        'metrics': {'clients': Client.objects.count(), 'projects': Project.objects.count(), 'quotesPending': Quote.objects.filter(status=Quote.Status.DRAFT).count(), 'activeSites': Site.objects.filter(status=Site.Status.IN_PROGRESS).count()},
        'recentProjects': list(Project.objects.order_by('-created_at').values('id', 'name', 'status', 'client')[:6]),
        'user': {'name': request.user.get_full_name() or request.user.username, 'role': request.user.groups.first().name if request.user.groups.exists() else 'Administrateur'},
        'projectsEvolution': {'monthly': monthly_data, 'quarterly': quarterly_data, 'semesterly': semesterly_data},
    })