from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from inertia import render
from business.models import Client, Project, Quote, Site

def health_check(request):
    """Endpoint léger pour le health check Render — aucune dépendance frontend."""
    return JsonResponse({'status': 'ok'})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('dashboard')
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