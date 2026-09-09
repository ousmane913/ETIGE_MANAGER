from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Client(TimestampedModel):
    company_name = models.CharField('raison sociale', max_length=180)
    contact_name = models.CharField('contact', max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40)
    address = models.TextField(blank=True)
    def __str__(self): return self.company_name

def generate_next_project_number():
    """Génère le prochain numéro de projet automatique ETIGE (ex: PRJ-001, PRJ-002)."""
    import re
    max_num = 0
    for p in Project.objects.exclude(project_number=''):
        match = re.search(r'(\d+)', p.project_number or '')
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1 if max_num > 0 else (Project.objects.count() + 1)
    return f'PRJ-{next_num:03d}'

class Project(TimestampedModel):
    class Status(models.TextChoices):
        SURVEY = 'SURVEY', 'Survey'
        QUOTATION = 'QUOTATION', 'Devis'
        PURCHASE = 'PURCHASE', 'Achats'
        SITE = 'SITE', 'Chantier'
        CLOSED = 'CLOSED', 'Clôturé'
    reference = models.CharField('Référence client', max_length=32)
    project_number = models.CharField('Numéro de projet (ETIGE)', max_length=64, unique=True, null=True, blank=True)
    name = models.CharField('Nom du projet', max_length=180)
    client = models.CharField('Client', max_length=180)
    address = models.TextField('Adresse')
    start_date = models.DateField('Date de début', null=True, blank=True)
    target_end_date = models.DateField('Échéance cible', null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SURVEY)
    manager = models.CharField('Manager', max_length=120, blank=True)

    def save(self, *args, **kwargs):
        if not self.project_number:
            self.project_number = generate_next_project_number()
        super().save(*args, **kwargs)

    def __str__(self): return f'{self.project_number} — {self.reference} — {self.name}'

class Survey(TimestampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='survey')
    visit_date = models.DateField()
    findings = models.TextField('constats')
    technical_notes = models.TextField('notes techniques', blank=True)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_validated = models.BooleanField(default=False)
    def __str__(self): return f'Survey {self.project.project_number or self.project.reference}'

class Quote(TimestampedModel):
    class Status(models.TextChoices):
        SENT = 'SENT', 'Envoyé'
        REJECTED = 'REJECTED', 'Refusé'
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='quote')
    number = models.CharField(max_length=40)
    amount_excl_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    adjusted_amount_excl_tax = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    validity_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SENT)
    notes = models.TextField(blank=True)
    def clean(self):
        # Le Survey n'est plus obligatoire. S'il existe et a été initié, il doit être validé.
        if hasattr(self.project, 'survey') and self.project.survey.pk and not self.project.survey.is_validated:
            raise ValidationError('Le Survey existant doit être validé avant la validation du devis.')
    @property
    def amount_incl_tax(self): return self.amount_excl_tax * (1 + self.vat_rate / 100)
    @property
    def final_adjusted_amount(self): return self.adjusted_amount_excl_tax if self.adjusted_amount_excl_tax is not None else self.amount_excl_tax
    def __str__(self): return self.number

class QuoteLine(TimestampedModel):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='lines')
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField('Unité', max_length=30, blank=True)
    designation = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    adjusted_unit_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    @property
    def amount(self): return self.quantity * self.unit_price
    @property
    def final_unit_price(self): return self.adjusted_unit_price if self.adjusted_unit_price is not None else self.unit_price
    @property
    def final_amount(self): return self.quantity * self.final_unit_price
    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La quantité doit être supérieure à zéro.'})
        if self.unit_price < Decimal('0'):
            raise ValidationError({'unit_price': 'Le prix unitaire ne peut pas être négatif.'})

class ProjectSchedule(TimestampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='schedule')
    start_date = models.DateField('Date de début', null=True, blank=True)
    end_date = models.DateField('Date de fin', null=True, blank=True)
    notes = models.TextField('Notes / Objectifs généraux', blank=True)

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days + 1
            return max(delta, 1)
        return None

    def __str__(self):
        return f'Planning {self.project.project_number or self.project.reference}'

class PlanningTask(TimestampedModel):
    class Status(models.TextChoices):
        TODO = 'TODO', 'À faire'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours'
        DONE = 'DONE', 'Terminé'

    schedule = models.ForeignKey(ProjectSchedule, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField('Phase / Étape', max_length=255)
    description = models.TextField('Déroulement / Détails des opérations', blank=True)
    start_date = models.DateField('Date de début', null=True, blank=True)
    end_date = models.DateField('Date de fin', null=True, blank=True)
    assigned_to = models.CharField('Responsable / Équipe', max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days + 1
            return max(delta, 1)
        return None

    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'

class Purchase(TimestampedModel):
    class Status(models.TextChoices):
        ORDERED = 'ORDERED', 'Commandé'
        RECEIVED = 'RECEIVED', 'Reçu'
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='purchases')
    reference = models.CharField(max_length=40)
    supplier = models.CharField(max_length=180)
    description = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ORDERED)
    ordered_on = models.DateField(null=True, blank=True)
    delivered_on = models.DateField(null=True, blank=True)
    def clean(self):
        if not hasattr(self.project, 'quote'):
            raise ValidationError('Le devis doit être créé avant tout achat.')
        if self.project.quote.status == Quote.Status.REJECTED:
            raise ValidationError('Le devis ne doit pas être refusé (REJECTED) pour pouvoir créer un achat.')
    def __str__(self): return self.reference

class Expense(TimestampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return f'{self.description} - {self.amount}'

class Site(TimestampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Non démarré'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours'
        COMPLETED = 'COMPLETED', 'Terminé'
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='site')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    supervisor_name = models.CharField('nom du superviseur', max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NOT_STARTED)
    progress = models.PositiveSmallIntegerField(default=0)
    started_on = models.DateField(null=True, blank=True)
    completed_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    def clean(self):
        if not self.project.purchases.exists():
            raise ValidationError('Au moins un achat doit être créé avant le démarrage du chantier.')
        if not self.project.purchases.filter(status=Purchase.Status.RECEIVED).exists():
            raise ValidationError('Au moins un achat doit être réceptionné (RECEIVED) avant le démarrage du chantier.')
        if not 0 <= self.progress <= 100:
            raise ValidationError({'progress': 'L’avancement doit être compris entre 0 et 100 %.'})
        self.status = self.status_for_progress(self.progress)
    def save(self, *args, **kwargs):
        self.status = self.status_for_progress(self.progress)
        super().save(*args, **kwargs)
    @staticmethod
    def status_for_progress(progress):
        if progress == 0:
            return Site.Status.NOT_STARTED
        if progress == 100:
            return Site.Status.COMPLETED
        return Site.Status.IN_PROGRESS
    def __str__(self): return f'Chantier {self.project.reference}'

class ClosureReport(TimestampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='closure_report')
    summary = models.TextField()
    lessons_learned = models.TextField(blank=True)
    final_budget = models.DecimalField('Budget Final', max_digits=14, decimal_places=2, null=True, blank=True)
    delivered_on = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    def clean(self):
        if not hasattr(self.project, 'site'):
            raise ValidationError('Le chantier doit être créé avant sa clôture.')
        if self.project.site.status != Site.Status.COMPLETED:
            raise ValidationError('Le chantier doit être terminé (COMPLETED) avant sa clôture.')
    def __str__(self): return f'Rapport {self.project.reference}'

class ProjectPhoto(TimestampedModel):
    class Category(models.TextChoices):
        SURVEY = 'SURVEY', 'Survey'
        CLOSURE = 'CLOSURE', 'Clôture'
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='photos')
    category = models.CharField(max_length=12, choices=Category.choices)
    image = models.ImageField(upload_to='projects/photos/')
    caption = models.CharField(max_length=180, blank=True)
    def __str__(self): return f'{self.project.reference} - {self.category} - {self.image.name}'
