import json
from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from inertia import render
from .forms import ClientForm, ProjectForm, SurveyForm, QuoteForm, PurchaseForm, SiteForm, ClosureReportForm
from .models import Client, Project, Survey, Quote, QuoteLine, Purchase, Site, ClosureReport, ProjectPhoto

def errors(form): return {field: [str(error) for error in field_errors] for field, field_errors in form.errors.items()}
def form_value(value):
    if value is None:
        return ''
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value).replace(',', '.')
    return str(value)

def form_props(form, title, action, subtitle=''):
    fields = []
    for name, field in form.fields.items():
        input_type = 'textarea' if field.widget.__class__.__name__ == 'Textarea' else getattr(field.widget, 'input_type', 'text')
        choices = [(str(value), str(label)) for value, label in field.choices] if getattr(field, 'choices', None) else None
        fields.append({'name': name, 'label': field.label, 'type': input_type, 'required': field.required, 'choices': choices, 'initial': form_value(form[name].value())})
    return {'title': title, 'subtitle': subtitle, 'action': action, 'fields': fields, 'errors': errors(form)}

def related_or_none(instance, relation):
    try:
        return getattr(instance, relation)
    except ObjectDoesNotExist:
        return None

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
@require_http_methods(['GET', 'POST'])
def client_edit(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    form = ClientForm(request.POST or None, instance=client)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Client modifié.')
        return redirect('clients')
    return render(request, 'Shared/Form', form_props(form, 'Modifier le client', f'/clients/{client.id}/modifier/', 'Mettez à jour les informations du client.'))

@login_required
@require_http_methods(['POST'])
def client_delete(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    client.delete()
    messages.success(request, 'Client supprimé.')
    return redirect('clients')

@login_required
def projects(request):
    data = list(Project.objects.order_by('-created_at').values('id', 'reference', 'name', 'status', 'client', 'budget', 'target_end_date'))
    return render(request, 'Projects/Index', {'projects': data, 'statuses': dict(Project.Status.choices)})

@login_required
@require_http_methods(['POST'])
def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, 'Projet supprimé.')
    return redirect('projects')

@login_required
@require_http_methods(['GET', 'POST'])
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(); messages.success(request, 'Projet créé : le Survey peut démarrer.'); return redirect('project-detail', project.id)
    return render(request, 'Shared/Form', form_props(form, 'Nouveau projet', '/projets/nouveau/', 'Le projet entre d’abord en phase Survey.'))

@login_required
@require_http_methods(['GET', 'POST'])
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Projet modifié.')
        return redirect('project-detail', project.id)
    return render(request, 'Shared/Form', form_props(form, 'Modifier le projet', f'/projets/{project.id}/modifier/', 'Mettez à jour les informations générales du projet.'))

def _detail_props(project):
    return {'project': {
        'id': project.id, 'reference': project.reference, 'name': project.name, 'address': project.address, 'status': project.status,
        'client': project.client, 'budget': str(project.budget), 'targetEndDate': project.target_end_date,
        'survey': related_or_none(project, 'survey') and {'validated': project.survey.is_validated, 'visitDate': project.survey.visit_date, 'findings': project.survey.findings},
        'quote': related_or_none(project, 'quote') and {'id': project.quote.id, 'number': project.quote.number, 'amount': str(project.quote.amount_excl_tax), 'status': project.quote.status, 'lines': [{'quantity': str(line.quantity), 'designation': line.designation, 'unitPrice': str(line.unit_price), 'amount': str(line.amount)} for line in project.quote.lines.all()]},
        'purchases': list(project.purchases.values('reference', 'supplier', 'amount', 'status')),
        'site': related_or_none(project, 'site') and {'status': project.site.status, 'progress': project.site.progress, 'notes': project.site.notes},
        'report': related_or_none(project, 'closure_report') and {'deliveredOn': project.closure_report.delivered_on, 'finalCost': str(project.closure_report.final_cost)},
        'photos': [{'url': photo.image.url, 'caption': photo.caption, 'category': photo.category} for photo in project.photos.all()],
    }}

@login_required
def project_detail(request, project_id):
    return render(request, 'Projects/Show', _detail_props(get_object_or_404(Project, pk=project_id)))

def _workflow_form(request, project_id, Form, model, title, phase, extra=None):
    project = get_object_or_404(Project, pk=project_id)
    # Inertia.js envoie les fichiers directement sous le nom 'photo_files' avec forceFormData
    # Pas besoin de logique d'indexation complexe
    relation = {Survey: 'survey', Quote: 'quote', Site: 'site', ClosureReport: 'closure_report'}.get(model)
    if model is Purchase and request.GET.get('nouveau') != '1':
        instance = project.purchases.order_by('-created_at').first()
    else:
        instance = related_or_none(project, relation) if relation else None
    if instance is None:
        instance = model(project=project)
    if model is Quote and not instance.number:
        instance.number = project.reference
    if model is Purchase and not instance.reference:
        instance.reference = project.reference
    form = Form(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        try:
            with transaction.atomic():
                record.full_clean(); record.save()
                if model is Survey:
                    for image in request.FILES.getlist('photo_files'):
                        photo = ProjectPhoto(project=project, category=ProjectPhoto.Category.SURVEY, image=image)
                        photo.full_clean(); photo.save()
                if model is ClosureReport:
                    for image in request.FILES.getlist('photo_files'):
                        photo = ProjectPhoto(project=project, category=ProjectPhoto.Category.CLOSURE, image=image)
                        photo.full_clean(); photo.save()
                if extra: extra(record, project)
            messages.success(request, f'{title} enregistré.'); return redirect('project-detail', project.id)
        except ValidationError as exc:
            form.add_error(None, exc)
    action = f'/projets/{project.id}/{phase}/'
    if model is Purchase and request.GET.get('nouveau') == '1':
        action += '?nouveau=1'
    return render(request, 'Shared/Form', form_props(form, title, action, f'Projet {project.reference} — {project.name}'))

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
    project = get_object_or_404(Project, pk=project_id)
    quote = related_or_none(project, 'quote') or Quote(project=project, number=project.reference)
    form = QuoteForm(request.POST or None, instance=quote)
    lines = [{'quantity': str(line.quantity), 'designation': line.designation, 'unitPrice': str(line.unit_price)} for line in quote.lines.all()] if quote.pk else []
    if request.method == 'POST':
        try:
            submitted_lines = json.loads(request.POST.get('lines', '[]'))
            if not isinstance(submitted_lines, list):
                raise ValueError
            lines = submitted_lines
            quote.amount_excl_tax = sum((Decimal(str(line.get('quantity', '0'))) * Decimal(str(line.get('unitPrice', '0'))) for line in submitted_lines if isinstance(line, dict)), Decimal('0'))
        except (InvalidOperation, TypeError, ValueError, json.JSONDecodeError):
            quote.amount_excl_tax = Decimal('0')
    if request.method == 'POST' and form.is_valid():
        raw_lines = request.POST.getlist('lines')
        if len(raw_lines) == 1 and isinstance(raw_lines[0], str):
            try:
                raw_lines = json.loads(raw_lines[0])
            except json.JSONDecodeError:
                raw_lines = []
        parsed_lines = []
        try:
            for index, raw_line in enumerate(raw_lines, start=1):
                if not isinstance(raw_line, dict) or not str(raw_line.get('designation', '')).strip():
                    raise ValueError(f'Désignation de la ligne {index} obligatoire.')
                if not str(raw_line.get('quantity', '')).strip():
                    raise ValueError(f'Quantité de la ligne {index} obligatoire.')
                if not str(raw_line.get('unitPrice', '')).strip():
                    raise ValueError(f'Prix unitaire de la ligne {index} obligatoire.')
                quantity = Decimal(str(raw_line['quantity']))
                if quantity != quantity.to_integral_value():
                    raise ValueError(f'La quantité de la ligne {index} doit être un nombre entier.')
                parsed_lines.append(QuoteLine(quantity=int(quantity), designation=str(raw_line['designation']).strip(), unit_price=Decimal(str(raw_line['unitPrice']))))
            if not parsed_lines:
                raise ValueError('Ajoutez au moins une ligne au devis.')
            total = sum((line.quantity * line.unit_price for line in parsed_lines), Decimal('0'))
            with transaction.atomic():
                record = form.save(commit=False)
                record.amount_excl_tax = total
                record.full_clean()
                record.save()
                record.lines.all().delete()
                for line in parsed_lines:
                    line.quote = record
                    line.full_clean()
                QuoteLine.objects.bulk_create(parsed_lines)
                if record.status == Quote.Status.APPROVED:
                    project.status = Project.Status.PURCHASE
                    project.save()
            messages.success(request, 'Devis enregistré.')
            return redirect('project-detail', project.id)
        except (InvalidOperation, ValueError, ValidationError) as exc:
            if isinstance(exc, ValidationError) and hasattr(exc, 'message_dict'):
                message = '; '.join(f'{field} : {" ".join(messages)}' for field, messages in exc.message_dict.items())
            else:
                message = str(exc)
            form.add_error(None, message)
    elif request.method == 'POST':
        for field_name, field_errors in list(form.errors.items()):
            for field_error in field_errors:
                if field_name != '__all__':
                    form.add_error(None, f'{form.fields[field_name].label if field_name in form.fields else field_name} : {field_error}')
    return render(request, 'Quote/Form', {'title': 'Devis', 'subtitle': f'Projet {project.reference} — {project.name}', 'action': f'/projets/{project.id}/devis/', 'fields': form_props(form, 'Devis', '', '')['fields'], 'errors': form_props(form, 'Devis', '', '')['errors'], 'lines': lines})

@login_required
@require_http_methods(['GET'])
def quote_pdf(request, project_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    project = get_object_or_404(Project, pk=project_id)
    quote = get_object_or_404(Quote, project=project)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 25 * mm
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(20 * mm, y, 'DEVIS')
    pdf.setFont('Helvetica', 10)
    y -= 10 * mm
    pdf.drawString(20 * mm, y, f'Projet : {project.name}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Client : {project.client}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Reference : {quote.number}')
    y -= 12 * mm
    pdf.drawString(20 * mm, y, f'Date de validite : {quote.validity_date.strftime("%d/%m/%Y") if quote.validity_date else "Non indiquee"}')
    y -= 12 * mm
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(20 * mm, y, 'Qte')
    pdf.drawString(40 * mm, y, 'Designation')
    pdf.drawString(125 * mm, y, 'Prix unitaire')
    pdf.drawString(165 * mm, y, 'Montant')
    y -= 6 * mm
    pdf.setFont('Helvetica', 9)
    for line in quote.lines.all():
        if y < 25 * mm:
            pdf.showPage()
            y = height - 20 * mm
        pdf.drawString(20 * mm, y, str(line.quantity))
        pdf.drawString(40 * mm, y, line.designation[:48])
        pdf.drawRightString(155 * mm, y, f'{line.unit_price:,.2f} FCFA')
        pdf.drawRightString(195 * mm, y, f'{line.amount:,.2f} FCFA')
        y -= 5 * mm
    y -= 5 * mm
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawRightString(195 * mm, y, f'Montant : {quote.amount_excl_tax:,.2f} FCFA')
    pdf.save()
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="devis-{quote.number}.pdf"'
    return response

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
