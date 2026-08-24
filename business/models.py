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

class Project(TimestampedModel):
    class Status(models.TextChoices):
        SURVEY = 'SURVEY', 'Survey'
        QUOTATION = 'QUOTATION', 'Devis'
        PURCHASE = 'PURCHASE', 'Achats'
        SITE = 'SITE', 'Chantier'
        CLOSED = 'CLOSED', 'Clôturé'
    reference = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=180)
    client = models.CharField('Client', max_length=180)
    address = models.TextField()
    start_date = models.DateField('Date de début', null=True, blank=True)
    target_end_date = models.DateField('Échéance cible', null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SURVEY)
    manager = models.CharField('Manager', max_length=120, blank=True)
    def __str__(self): return f'{self.reference} — {self.name}'

class Survey(TimestampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='survey')
    visit_date = models.DateField()
    findings = models.TextField('constats')
    technical_notes = models.TextField('notes techniques', blank=True)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_validated = models.BooleanField(default=False)
    def __str__(self): return f'Survey {self.project.reference}'

class Quote(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        SENT = 'SENT', 'Envoyé'
        APPROVED = 'APPROVED', 'Validé'
        REJECTED = 'REJECTED', 'Refusé'
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='quote')
    number = models.CharField(max_length=40)
    amount_excl_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    validity_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    def clean(self):
        if not hasattr(self.project, 'survey'):
            raise ValidationError('Le Survey doit être créé avant la création du devis.')
        if not self.project.survey.is_validated:
            raise ValidationError('Le Survey doit être validé avant la création du devis.')
    @property
    def amount_incl_tax(self): return self.amount_excl_tax * (1 + self.vat_rate / 100)
    def __str__(self): return self.number

class QuoteLine(TimestampedModel):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='lines')
    quantity = models.PositiveIntegerField(default=1)
    designation = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    @property
    def amount(self): return self.quantity * self.unit_price
    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La quantité doit être supérieure à zéro.'})
        if self.unit_price < Decimal('0'):
            raise ValidationError({'unit_price': 'Le prix unitaire ne peut pas être négatif.'})

class Purchase(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        ORDERED = 'ORDERED', 'Commandé'
        RECEIVED = 'RECEIVED', 'Reçu'
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='purchases')
    reference = models.CharField(max_length=40)
    supplier = models.CharField(max_length=180)
    description = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    ordered_on = models.DateField(null=True, blank=True)
    delivered_on = models.DateField(null=True, blank=True)
    def clean(self):
        if not hasattr(self.project, 'quote'):
            raise ValidationError('Le devis doit être créé avant tout achat.')
        if self.project.quote.status != Quote.Status.APPROVED:
            raise ValidationError('Le devis doit être validé (APPROVED) avant tout achat.')
    def __str__(self): return self.reference

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
    final_cost = models.DecimalField(max_digits=14, decimal_places=2)
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
