import json
from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db import transaction, models
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from inertia import render
from .forms import ClientForm, ProjectForm, SurveyForm, QuoteForm, PurchaseForm, SiteForm, ClosureReportForm, ExpenseForm, ProjectScheduleForm, ProjectDocumentForm
from .models import Client, Project, Survey, Quote, QuoteLine, Purchase, PurchaseLine, Site, ClosureReport, ProjectPhoto, ProjectDocument, Expense, ProjectSchedule, PlanningTask, peek_next_project_number
from .permissions import (
    can_delete_client,
    can_delete_project,
    can_edit_project,
    can_view_financials,
    MSG_DG_ONLY_DELETE_CLIENT,
    MSG_DG_ONLY_DELETE_PROJECT,
    MSG_DG_ONLY_EDIT,
    require_permission,
    role_flags,
)

def errors(form): return {field: [str(error) for error in field_errors] for field, field_errors in form.errors.items()}
def form_value(value):
    if value is None:
        return ''
    if isinstance(value, Decimal):
        return str(value).replace(',', '.')
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if hasattr(value, 'pk'):
        return str(value.pk)
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
    return render(request, 'Clients/Index', {
        'clients': list(Client.objects.order_by('company_name').values('id', 'company_name', 'contact_name', 'email', 'phone')),
        **role_flags(request.user),
    })

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
@require_permission(can_delete_client, MSG_DG_ONLY_DELETE_CLIENT, fallback='clients')
def client_delete(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    try:
        client.delete()
    except ProtectedError:
        messages.error(request, 'Impossible de supprimer ce client : des projets y sont encore liés.')
        return redirect('clients')
    messages.success(request, 'Client supprimé.')
    return redirect('clients')

@login_required
def projects(request):
    query = request.GET.get('q', '').strip()
    qs = Project.objects.select_related('client').order_by('-created_at')
    if query:
        qs = qs.filter(
            models.Q(project_number__icontains=query) |
            models.Q(reference__icontains=query) |
            models.Q(name__icontains=query) |
            models.Q(client__company_name__icontains=query)
        )
    show_budget = can_view_financials(request.user)
    data = [{
        'id': project.id,
        'project_number': project.project_number,
        'reference': project.reference,
        'name': project.name,
        'status': project.status,
        'client': project.client_name,
        'budget': project.budget if show_budget else None,
        'target_end_date': project.target_end_date,
    } for project in qs]
    return render(request, 'Projects/Index', {
        'projects': data,
        'statuses': dict(Project.Status.choices),
        'searchQuery': query,
        **role_flags(request.user),
    })

@login_required
@require_http_methods(['POST'])
@require_permission(can_delete_project, MSG_DG_ONLY_DELETE_PROJECT)
def project_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, 'Projet supprimé.')
    return redirect('projects')

@login_required
@require_http_methods(['GET', 'POST'])
def project_create(request):
    is_management = can_view_financials(request.user)
    initial = {'project_number': peek_next_project_number()}
    form = ProjectForm(request.POST or None, initial=initial)
    if not is_management:
        if 'budget' in form.fields: del form.fields['budget']
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        if not is_management:
            project.budget = 0
        project.save()
        messages.success(request, f'Projet {project.project_number} créé avec succès.')
        return redirect('project-detail', project.id)
    return render(request, 'Shared/Form', form_props(form, 'Nouveau projet', '/projets/nouveau/', 'Créez un projet avec son numéro ETIGE et sa référence client.'))

@login_required
@require_http_methods(['GET', 'POST'])
@require_permission(can_edit_project, MSG_DG_ONLY_EDIT)
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Projet modifié.')
        return redirect('project-detail', project.id)
    return render(request, 'Shared/Form', form_props(form, 'Modifier le projet', f'/projets/{project.id}/modifier/', f'Projet {project.project_number or project.reference} — {project.name}'))

def _detail_props(request, project):
    flags = role_flags(request.user)
    is_dg = flags['isDg']
    is_dt = flags['isDt']
    is_management = flags['isManagement']

    total_purchases = sum(p.amount for p in project.purchases.all())
    total_expenses = sum(e.amount for e in project.expenses.all())
    final_cost = total_purchases + total_expenses

    # Budget Final saisi par DG/DT dans le formulaire de clôture
    report = related_or_none(project, 'closure_report')
    final_budget = report.final_budget if report and report.final_budget else None
    quote = project.quotes.filter(status='ACCEPTED').first()
    schedule = related_or_none(project, 'schedule')

    profit = None
    if final_budget is not None:
        profit = float(final_budget) - float(final_cost)

    return {'project': {
        'id': project.id,
        'projectNumber': project.project_number or project.reference,
        'reference': project.reference,
        'name': project.name,
        'address': project.address,
        'status': project.status,
        'client': project.client_name,
        'clientEmail': project.client_email,
        'targetEndDate': project.target_end_date,
        'isManagement': is_management,
        'isDg': is_dg,
        'isDt': is_dt,
        'estimatedBudget': str(project.budget) if is_management and project.budget else None,
        'budget': str(final_budget) if is_management and final_budget else None,
        'finalCost': str(final_cost) if is_management else None,
        'profit': str(profit) if is_management and profit is not None else None,
        'survey': related_or_none(project, 'survey') and {'validated': project.survey.is_validated, 'visitDate': project.survey.visit_date, 'findings': project.survey.findings},
        'quote': quote and {
            'id': quote.id, 'number': quote.number,
            'amount': str(quote.amount_excl_tax),
            'adjustedAmount': str(quote.final_adjusted_amount) if is_management else None,
            'status': quote.status,
            'lines': [{'quantity': str(line.quantity), 'unit': line.unit or 'u', 'designation': line.designation, 'unitPrice': str(line.unit_price), 'adjustedUnitPrice': str(line.adjusted_unit_price) if is_management and line.adjusted_unit_price is not None else None, 'amount': str(line.amount)} for line in quote.lines.all()]
        },
        'quotes': [{'id': q.id, 'number': q.number, 'amount': str(q.final_adjusted_amount), 'status': q.status, 'date': q.created_at.isoformat()} for q in project.quotes.all().order_by('-created_at')],
        'documents': [{'id': d.id, 'name': d.name, 'category': d.category, 'url': d.file.url, 'uploadedBy': d.uploaded_by.username if d.uploaded_by else '', 'date': d.created_at.isoformat()} for d in project.documents.all().order_by('-created_at')],
        'schedule': schedule and {
            'startDate': schedule.start_date,
            'endDate': schedule.end_date,
            'notes': schedule.notes,
            'tasksCount': schedule.tasks.count(),
            'completedTasksCount': schedule.tasks.filter(status='DONE').count(),
        },
        'purchases': [{'id': p.id, 'reference': p.reference, 'supplier': p.supplier, 'amount': str(p.amount), 'status': p.status, 'ordered_on': p.ordered_on, 'lines': [{'designation': l.designation, 'quantity': l.quantity, 'unitPrice': str(l.unit_price), 'amount': str(l.amount)} for l in p.lines.all()]} for p in project.purchases.all().order_by('-created_at')],
        'expenses': list(project.expenses.values('description', 'amount', 'date', 'created_at')),
        'site': related_or_none(project, 'site') and {'status': project.site.status, 'progress': project.site.progress, 'notes': project.site.notes},
        'report': report and {'deliveredOn': report.delivered_on},
        'photos': [{'url': photo.image.url, 'caption': photo.caption, 'category': photo.category} for photo in project.photos.all()],
    }}

@login_required
def project_detail(request, project_id):
    return render(request, 'Projects/Show', _detail_props(request, get_object_or_404(Project.objects.select_related('client'), pk=project_id)))

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
def quote_create(request, project_id, quote_id=None):
    project = get_object_or_404(Project.objects.select_related('client'), pk=project_id)
    if quote_id:
        quote = get_object_or_404(Quote, project=project, pk=quote_id)
    else:
        count = project.quotes.count() + 1
        quote = Quote(project=project, number=f"{project.project_number or project.reference}-V{count}")
    form = QuoteForm(request.POST or None, instance=quote)
    is_management = can_view_financials(request.user)
    lines = [{'quantity': str(line.quantity), 'unit': line.unit or 'u', 'designation': line.designation, 'unitPrice': str(line.unit_price)} for line in quote.lines.all()] if quote.pk else []
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
                
                unit = str(raw_line.get('unit', 'u')).strip() or 'u'
                unit_price = Decimal(str(raw_line['unitPrice']))

                parsed_lines.append(QuoteLine(quantity=int(quantity), unit=unit, designation=str(raw_line['designation']).strip(), unit_price=unit_price, adjusted_unit_price=unit_price))
            if not parsed_lines:
                raise ValueError('Ajoutez au moins une ligne au devis.')
            total = sum((line.quantity * line.unit_price for line in parsed_lines), Decimal('0'))
            with transaction.atomic():
                record = form.save(commit=False)
                record.amount_excl_tax = total
                record.adjusted_amount_excl_tax = total
                record.full_clean()
                record.save()
                record.lines.all().delete()
                for line in parsed_lines:
                    line.quote = record
                    line.full_clean()
                QuoteLine.objects.bulk_create(parsed_lines)
                
                if project.status == Project.Status.SURVEY:
                    project.status = Project.Status.QUOTATION
                    project.save()

                if record.status == Quote.Status.SENT:
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
    return render(request, 'Quote/Form', {
        'title': 'Devis',
        'subtitle': f'N° {project.project_number or project.reference} — Réf {project.reference} — Client {project.client_name}',
        'action': f'/projets/{project.id}/devis/{quote.id}/' if quote.pk else f'/projets/{project.id}/devis/',
        'fields': form_props(form, 'Devis', '', '')['fields'],
        'errors': form_props(form, 'Devis', '', '')['errors'],
        'lines': lines,
        'is_management': is_management,
        'project': {
            'id': project.id,
            'name': project.name,
            'projectNumber': project.project_number or project.reference,
            'reference': project.reference,
            'client': project.client_name,
        }
    })

def _fmt_fcfa(amount):
    """Formate un montant FCFA : sans decimales, separateur de milliers = point.
    Ex: 1500000 -> '1.500.000'
    """
    return f"{int(round(amount)):,}".replace(',', '.')

def _build_quote_pdf_bytes(project, quote):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 25 * mm
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(20 * mm, y, 'DEVIS')
    pdf.setFont('Helvetica', 10)
    y -= 8 * mm
    pdf.drawString(20 * mm, y, f'N° Projet ETIGE : {project.project_number or "-"}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Reference Client : {project.reference}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Client : {project.client_name}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Nom du projet : {project.name}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Numero de devis : {quote.number}')
    y -= 8 * mm
    pdf.drawString(20 * mm, y, f'Date de validite : {quote.validity_date.strftime("%d/%m/%Y") if quote.validity_date else "Non indiquee"}')
    y -= 10 * mm
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(20 * mm, y, 'Qte')
    pdf.drawString(34 * mm, y, 'Unite')
    pdf.drawString(52 * mm, y, 'Designation')
    pdf.drawRightString(150 * mm, y, 'Prix unitaire')
    pdf.drawRightString(195 * mm, y, 'Montant')
    y -= 6 * mm
    pdf.setFont('Helvetica', 9)
    for line in quote.lines.all():
        if y < 25 * mm:
            pdf.showPage()
            y = height - 20 * mm
        pdf.drawString(20 * mm, y, str(line.quantity))
        pdf.drawString(34 * mm, y, str(line.unit or 'u')[:8])
        pdf.drawString(52 * mm, y, line.designation[:38])
        pdf.drawRightString(150 * mm, y, f'{_fmt_fcfa(line.final_unit_price)} FCFA')
        pdf.drawRightString(195 * mm, y, f'{_fmt_fcfa(line.final_amount)} FCFA')
        y -= 5 * mm
    y -= 5 * mm
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawRightString(195 * mm, y, f'TOTAL : {_fmt_fcfa(quote.final_adjusted_amount)} FCFA')
    pdf.save()
    return buffer.getvalue()

@login_required
@require_http_methods(['GET'])
def quote_pdf(request, project_id, quote_id):
    project = get_object_or_404(Project, pk=project_id)
    quote = get_object_or_404(Quote, project=project, pk=quote_id)
    pdf_data = _build_quote_pdf_bytes(project, quote)
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="devis-{quote.number}.pdf"'
    return response

@login_required
@require_http_methods(['POST'])
def quote_send_email(request, project_id, quote_id):
    project = get_object_or_404(Project, pk=project_id)
    # Try to fetch an existing Quote; if none exists, inform the user
    quote = get_object_or_404(Quote, project=project, pk=quote_id)
    if not quote:
        messages.error(request, 'Aucun devis trouvé pour ce projet. Veuillez d’abord créer un devis.')
        return redirect('project-detail', project.id)

    recipient_email = request.POST.get('email', '').strip()
    if not recipient_email:
        recipient_email = project.client_email

    if not recipient_email:
        messages.error(request, 'Veuillez renseigner une adresse email pour le client.')
        return redirect('project-detail', project.id)

    try:
        pdf_data = _build_quote_pdf_bytes(project, quote)
        subject = f"ETIGE - Devis {quote.number} - {project.name}"
        body = (
            f"Bonjour,\n\n"
            f"Veuillez trouver ci-joint le devis N° {quote.number} relatif au projet « {project.name} ».\n"
            f"• Numéro de projet ETIGE : {project.project_number or '-'}\n"
            f"• Référence client : {project.reference}\n"
            f"• Montant total : {quote.final_adjusted_amount:,.2f} FCFA\n\n"
            f"Restant à votre entière disposition pour tout complément d'information.\n\n"
            f"Cordialement,\n"
            f"L'équipe ETIGE\n"
        )
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach(f"devis-{quote.number}.pdf", pdf_data, 'application/pdf')
        email.send(fail_silently=False)



        quote.status = Quote.Status.SENT
        quote.save(update_fields=['status'])
        messages.success(request, f'Devis envoyé avec succès à {recipient_email}.')
    except Exception as exc:
        messages.error(request, f"Erreur lors de l'envoi de l'email : {exc}")

    return redirect('project-detail', project.id)

@login_required
@require_http_methods(['GET', 'POST'])
def project_planning(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    flags = role_flags(request.user)
    is_dg = flags['isDg']
    is_dt = flags['isDt']
    schedule, _ = ProjectSchedule.objects.get_or_create(project=project)

    if request.method == 'POST':
        schedule.start_date = request.POST.get('start_date') or None
        schedule.end_date = request.POST.get('end_date') or None
        schedule.notes = request.POST.get('notes', '')
        schedule.save()

        raw_tasks = request.POST.get('tasks', '[]')
        try:
            if isinstance(raw_tasks, str):
                tasks_data = json.loads(raw_tasks)
            else:
                tasks_data = raw_tasks
            if isinstance(tasks_data, list):
                schedule.tasks.all().delete()
                new_tasks = []
                for t in tasks_data:
                    if isinstance(t, dict) and str(t.get('name', '')).strip():
                        new_tasks.append(PlanningTask(
                            schedule=schedule,
                            name=str(t.get('name', '')).strip(),
                            description=str(t.get('description', '')).strip(),
                            start_date=t.get('startDate') or t.get('start_date') or None,
                            end_date=t.get('endDate') or t.get('end_date') or None,
                            assigned_to=str(t.get('assignedTo') or t.get('assigned_to') or '').strip(),
                            status=t.get('status') or 'TODO'
                        ))
                PlanningTask.objects.bulk_create(new_tasks)
            # Update site progress if site exists
            if hasattr(project, 'site'):
                total = schedule.tasks.count()
                done = schedule.tasks.filter(status='DONE').count()
                if total > 0:
                    progress = int((done / total) * 100)
                    project.site.progress = progress
                    project.site.save()

            messages.success(request, 'Planning enregistré avec succès.')
            return redirect('project-detail', project.id)
        except Exception as exc:
            messages.error(request, f'Erreur lors de l’enregistrement des phases : {exc}')

    return render(request, 'Projects/Planning', {
        'project': {
            'id': project.id,
            'name': project.name,
            'projectNumber': project.project_number or project.reference,
            'reference': project.reference,
            'client': project.client_name,
        },
        'schedule': {
            'startDate': schedule.start_date.isoformat() if schedule.start_date else '',
            'endDate': schedule.end_date.isoformat() if schedule.end_date else '',
            'durationDays': schedule.duration_days,
            'notes': schedule.notes,
        },
        'tasks': [{
            'name': t.name,
            'description': t.description,
            'startDate': t.start_date.isoformat() if t.start_date else '',
            'endDate': t.end_date.isoformat() if t.end_date else '',
            'durationDays': t.duration_days,
            'assignedTo': t.assigned_to,
            'status': t.status
        } for t in schedule.tasks.all()],
        'statusChoices': list(PlanningTask.Status.choices),
        'isDg': is_dg,
        'isDt': is_dt,
    })

@login_required
@require_http_methods(['GET'])
def planning_pdf(request, project_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    project = get_object_or_404(Project, pk=project_id)
    schedule = related_or_none(project, 'schedule')
    if not schedule:
        messages.error(request, 'Le planning n’a pas encore été établi pour ce projet.')
        return redirect('project-detail', project.id)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 25 * mm

    # En-tête officiel ETIGE
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(20 * mm, y, 'PLANNING PREVISIONNEL D’EXECUTION')
    pdf.setFont('Helvetica', 10)
    y -= 8 * mm
    pdf.drawString(20 * mm, y, f'N° Projet ETIGE : {project.project_number or "-"}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Reference Client : {project.reference}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Client : {project.client_name}')
    y -= 5 * mm
    pdf.drawString(20 * mm, y, f'Nom du projet : {project.name}')
    y -= 5 * mm
    start_str = schedule.start_date.strftime("%d/%m/%Y") if schedule.start_date else "Non definie"
    end_str = schedule.end_date.strftime("%d/%m/%Y") if schedule.end_date else "Non definie"
    duration_str = f" ({schedule.duration_days} jours)" if schedule.duration_days else ""
    pdf.drawString(20 * mm, y, f'Periode globale prevue : Du {start_str} au {end_str}{duration_str}')

    if schedule.notes:
        y -= 6 * mm
        pdf.setFont('Helvetica-Oblique', 9)
        pdf.drawString(20 * mm, y, f'Notes : {schedule.notes[:90]}')

    y -= 10 * mm
    # Tableau des phases / déroulement
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(20 * mm, y, 'Phase / Etape')
    pdf.drawString(65 * mm, y, 'Deroulement & Operations')
    pdf.drawString(130 * mm, y, 'Dates prevues')
    pdf.drawString(168 * mm, y, 'Resp.')
    pdf.drawString(185 * mm, y, 'Statut')
    y -= 3 * mm
    pdf.line(20 * mm, y, 195 * mm, y)
    y -= 6 * mm

    pdf.setFont('Helvetica', 9)
    status_map = {'TODO': 'A faire', 'IN_PROGRESS': 'En cours', 'DONE': 'Termine'}
    tasks = schedule.tasks.all()

    for index, task in enumerate(tasks, start=1):
        if y < 25 * mm:
            pdf.showPage()
            y = height - 20 * mm
        t_start = task.start_date.strftime("%d/%m/%Y") if task.start_date else "-"
        t_end = task.end_date.strftime("%d/%m/%Y") if task.end_date else "-"
        t_duration = f" ({task.duration_days}j)" if task.duration_days else ""

        pdf.setFont('Helvetica-Bold', 9)
        pdf.drawString(20 * mm, y, f'{index}. {task.name[:22]}')
        pdf.setFont('Helvetica', 8)
        pdf.drawString(65 * mm, y, task.description[:38] if task.description else "-")
        pdf.drawString(130 * mm, y, f'{t_start} -> {t_end}{t_duration}')
        pdf.drawString(168 * mm, y, (task.assigned_to or "-")[:10])
        pdf.drawString(185 * mm, y, status_map.get(task.status, task.status))
        y -= 6 * mm

    pdf.save()
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="planning-{project.project_number or project.reference}.pdf"'
    return response

@login_required
@require_http_methods(['GET', 'POST'])
def purchase_create(request, project_id, purchase_id=None):
    project = get_object_or_404(Project, pk=project_id)
    if purchase_id:
        purchase = get_object_or_404(Purchase, project=project, pk=purchase_id)
    else:
        purchase = Purchase(project=project, reference=project.reference)
    
    form = PurchaseForm(request.POST or None, instance=purchase)
    lines = [{'quantity': str(line.quantity), 'unit': line.unit or 'u', 'designation': line.designation, 'unitPrice': str(line.unit_price)} for line in purchase.lines.all()] if purchase.pk else []
    
    if request.method == 'POST':
        try:
            submitted_lines = json.loads(request.POST.get('lines', '[]'))
            if not isinstance(submitted_lines, list):
                raise ValueError
            lines = submitted_lines
            purchase.amount = sum((Decimal(str(line.get('quantity', '0'))) * Decimal(str(line.get('unitPrice', '0'))) for line in submitted_lines if isinstance(line, dict)), Decimal('0'))
        except (InvalidOperation, TypeError, ValueError, json.JSONDecodeError):
            purchase.amount = Decimal('0')
            
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
                quantity = Decimal(str(raw_line.get('quantity', '1')))
                unit_price = Decimal(str(raw_line.get('unitPrice', '0')))
                parsed_lines.append(PurchaseLine(quantity=int(quantity), unit=str(raw_line.get('unit', 'u'))[:30], designation=str(raw_line['designation'])[:255], unit_price=unit_price))
            if not parsed_lines:
                raise ValueError('Ajoutez au moins une ligne d\'achat.')
            total = sum((line.quantity * line.unit_price for line in parsed_lines), Decimal('0'))
            with transaction.atomic():
                record = form.save(commit=False)
                record.amount = total
                record.full_clean()
                record.save()
                record.lines.all().delete()
                for line in parsed_lines:
                    line.purchase = record
                    line.full_clean()
                PurchaseLine.objects.bulk_create(parsed_lines)
                
                if record.status == Purchase.Status.RECEIVED:
                    project.status = Project.Status.SITE
                    project.save()
            messages.success(request, 'Achat enregistré.')
            return redirect('project-detail', project.id)
        except (InvalidOperation, ValueError, ValidationError) as exc:
            if isinstance(exc, ValidationError) and hasattr(exc, 'message_dict'):
                message = '; '.join(f'{field} : {" ".join(msgs)}' for field, msgs in exc.message_dict.items())
            else:
                message = str(exc)
            form.add_error(None, message)
            
    return render(request, 'Purchase/Form', {
        'title': 'Achat',
        'subtitle': f'Projet {project.reference} — {project.name}',
        'action': f'/projets/{project.id}/achats/{purchase.id}/' if purchase.pk else f'/projets/{project.id}/achats/',
        'fields': form_props(form, 'Achat', '', '')['fields'],
        'errors': form_props(form, 'Achat', '', '')['errors'],
        'lines': lines,
    })

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

@login_required
@require_http_methods(['GET', 'POST'])
def expense_create(request, project_id):
    def advance(record, project):
        record.created_by = request.user
    return _workflow_form(request, project_id, ExpenseForm, Expense, 'Dépense Supplémentaire', 'depense', advance)

@login_required
@require_http_methods(['POST'])
def document_upload(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectDocumentForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.project = project
        doc.uploaded_by = request.user
        doc.save()
        messages.success(request, 'Document ajouté avec succès.')
    else:
        messages.error(request, 'Erreur lors de l\'ajout du document.')
    return redirect('project-detail', project.id)

@login_required
@require_http_methods(['POST'])
def document_delete(request, document_id):
    doc = get_object_or_404(ProjectDocument, pk=document_id)
    project_id = doc.project_id
    doc.delete()
    messages.success(request, 'Document supprimé.')
    return redirect('project-detail', project_id)
