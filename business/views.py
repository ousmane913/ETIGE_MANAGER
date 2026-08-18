from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from inertia import render
from .forms import ClientForm, ProjectForm, SurveyForm, QuoteForm, PurchaseForm, SiteForm, ClosureReportForm
from .models import Client, Project, Survey, Quote, Purchase, Site, ClosureReport

def errors(form): return {field: [str(error) for error in field_errors] for field, field_errors in form.errors.items()}
def form_props(form, title, action, subtitle=''):
    fields = []
    for name, field in form.fields.items():
        input_type = 'textarea' if field.widget.__class__.__name__ == 'Textarea' else getattr(field.widget, 'input_type', 'text')
        choices = [(str(value), str(label)) for value, label in field.choices] if getattr(field, 'choices', None) else None
        fields.append({'name': name, 'label': field.label, 'type': input_type, 'required': field.required, 'choices': choices})
    return {'title': title, 'subtitle': subtitle, 'action': action, 'fields': fields, 'errors': errors(form)}

@login_required
@require_http_methods(['GET'])
def clients(request):
    return render(request, 'Clients/Index', {'clients': list(Client.objects.order_by('company_name').values('id', 'company_name', 'contact_name', 'email', 'phone'))})

@login_required
@require_http_methods(['GET', 'POST'])
def client_create(request):
    form = ClientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Client créé.'); return redirect('clients')
    return render(request, 'Shared/Form', form_props(form, 'Nouveau client', '/clients/nouveau/', 'Enregistrez les informations du maître d’ouvrage.'))

@login_required
def projects(request):
    data = list(Project.objects.select_related('client').order_by('-created_at').values('id', 'reference', 'name', 'status', 'client__company_name', 'budget', 'target_end_date'))
    return render(request, 'Projects/Index', {'projects': data, 'statuses': dict(Project.Status.choices)})

@login_required
@require_http_methods(['GET', 'POST'])
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(); messages.success(request, 'Projet créé : le Survey peut démarrer.'); return redirect('project-detail', project.id)
    return render(request, 'Shared/Form', form_props(form, 'Nouveau projet', '/projets/nouveau/', 'Le projet entre d’abord en phase Survey.'))

def _detail_props(project):
    return {'project': {
        'id': project.id, 'reference': project.reference, 'name': project.name, 'address': project.address, 'status': project.status,
        'client': project.client.company_name, 'budget': str(project.budget), 'targetEndDate': project.target_end_date,
        'survey': getattr(project, 'survey', None) and {'validated': project.survey.is_validated, 'visitDate': project.survey.visit_date, 'findings': project.survey.findings},
        'quote': getattr(project, 'quote', None) and {'number': project.quote.number, 'amount': str(project.quote.amount_excl_tax), 'status': project.quote.status},
        'purchases': list(project.purchases.values('reference', 'supplier', 'amount', 'status')),
        'site': getattr(project, 'site', None) and {'status': project.site.status, 'progress': project.site.progress, 'notes': project.site.notes},
        'report': getattr(project, 'closure_report', None) and {'deliveredOn': project.closure_report.delivered_on, 'finalCost': str(project.closure_report.final_cost)},
    }}

@login_required
def project_detail(request, project_id):
    return render(request, 'Projects/Show', _detail_props(get_object_or_404(Project.objects.select_related('client'), pk=project_id)))

def _workflow_form(request, project_id, Form, model, title, phase, extra=None):
    project = get_object_or_404(Project, pk=project_id)
    instance = getattr(project, {Survey: 'survey', Quote: 'quote', Site: 'site', ClosureReport: 'closure_report'}.get(model, '_missing'), None)
    form = Form(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False); record.project = project
        try:
            record.full_clean(); record.save()
            if extra: extra(record, project)
            messages.success(request, f'{title} enregistré.'); return redirect('project-detail', project.id)
        except ValidationError as exc:
            form.add_error(None, exc)
    return render(request, 'Shared/Form', form_props(form, title, f'/projets/{project.id}/{phase}/', f'Projet {project.reference} — {project.name}'))

@login_required
@require_http_methods(['GET', 'POST'])
def survey_create(request, project_id):
    def advance(record, project):
        if record.is_validated:
            project.status = Project.Status.QUOTATION
            project.save()
    return _workflow_form(request, project_id, SurveyForm, Survey, 'Survey', 'survey', advance)

@login_required
@require_http_methods(['GET', 'POST'])
def quote_create(request, project_id):
    def advance(record, project):
        if record.status == Quote.Status.APPROVED: project.status = Project.Status.PURCHASE; project.save()
    return _workflow_form(request, project_id, QuoteForm, Quote, 'Devis', 'devis', advance)

@login_required
@require_http_methods(['GET', 'POST'])
def purchase_create(request, project_id):
    def advance(record, project):
        if record.status == Purchase.Status.RECEIVED: project.status = Project.Status.SITE; project.save()
    return _workflow_form(request, project_id, PurchaseForm, Purchase, 'Achat', 'achats', advance)

@login_required
@require_http_methods(['GET', 'POST'])
def site_create(request, project_id):
    return _workflow_form(request, project_id, SiteForm, Site, 'Chantier', 'chantier')

@login_required
@require_http_methods(['GET', 'POST'])
def closure_create(request, project_id):
    def advance(record, project):
        project.status = Project.Status.CLOSED
        project.save()
    return _workflow_form(request, project_id, ClosureReportForm, ClosureReport, 'Rapport de clôture', 'cloture', advance)
