from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

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

class Project(TimestampedModel):
    class Status(models.TextChoices):
        SURVEY = 'SURVEY', 'Survey'
        QUOTATION = 'QUOTATION', 'Devis'
        PURCHASE = 'PURCHASE', 'Achats'
        SITE = 'SITE', 'Chantier'
        CLOSED = 'CLOSED', 'Clôturé'
    reference = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=180)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='projects')
    address = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SURVEY)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='managed_projects')
    def __str__(self): return f'{self.reference} — {self.name}'

class Survey(TimestampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='survey')
    visit_date = models.DateField()
    findings = models.TextField('constats')
    technical_notes = models.TextField('notes techniques', blank=True)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    is_validated = models.BooleanField(default=False)
    def __str__(self): return f'Survey {self.project.reference}'

class Quote(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        SENT = 'SENT', 'Envoyé'
        APPROVED = 'APPROVED', 'Validé'
        REJECTED = 'REJECTED', 'Refusé'
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='quote')
    number = models.CharField(max_length=40, unique=True)
    amount_excl_tax = models.DecimalField(max_digits=14, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    validity_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    def clean(self):
        if not hasattr(self.project, 'survey') or not self.project.survey.is_validated:
            raise ValidationError('Le Survey doit être validé avant la création du devis.')
    @property
    def amount_incl_tax(self): return self.amount_excl_tax * (1 + self.vat_rate / 100)
    def __str__(self): return self.number

class Purchase(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        ORDERED = 'ORDERED', 'Commandé'
        RECEIVED = 'RECEIVED', 'Reçu'
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='purchases')
    reference = models.CharField(max_length=40, unique=True)
    supplier = models.CharField(max_length=180)
    description = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    ordered_on = models.DateField(null=True, blank=True)
    def clean(self):
        if not hasattr(self.project, 'quote') or self.project.quote.status != Quote.Status.APPROVED:
            raise ValidationError('Le devis doit être validé avant tout achat.')
    def __str__(self): return self.reference

class Site(TimestampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Non démarré'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours'
        COMPLETED = 'COMPLETED', 'Terminé'
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='site')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NOT_STARTED)
    progress = models.PositiveSmallIntegerField(default=0)
    started_on = models.DateField(null=True, blank=True)
    completed_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    def clean(self):
        if not self.project.purchases.filter(status=Purchase.Status.RECEIVED).exists():
            raise ValidationError('Au moins un achat doit être réceptionné avant le démarrage du chantier.')
    def __str__(self): return f'Chantier {self.project.reference}'

class ClosureReport(TimestampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='closure_report')
    summary = models.TextField()
    lessons_learned = models.TextField(blank=True)
    final_cost = models.DecimalField(max_digits=14, decimal_places=2)
    delivered_on = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    def clean(self):
        if not hasattr(self.project, 'site') or self.project.site.status != Site.Status.COMPLETED:
            raise ValidationError('Le chantier doit être terminé avant sa clôture.')
    def __str__(self): return f'Rapport {self.project.reference}'
