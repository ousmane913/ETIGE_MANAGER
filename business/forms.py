from django import forms
from .models import Client, Project, Survey, Quote, Purchase, Site, ClosureReport

class DateInput(forms.DateInput): input_type = 'date'
class MultipleFileInput(forms.ClearableFileInput): allow_multiple_selected = True
class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super().clean(file, initial) for file in files]
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client; fields = ['company_name', 'contact_name', 'email', 'phone', 'address']
        labels = {'company_name': 'Raison sociale', 'contact_name': 'Nom du contact', 'email': 'Email', 'phone': 'Téléphone', 'address': 'Adresse'}
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project; fields = ['reference', 'name', 'client', 'address', 'start_date', 'target_end_date', 'budget', 'manager']
        widgets = {'start_date': DateInput(), 'target_end_date': DateInput()}
        labels = {'reference': 'Référence', 'name': 'Nom du projet', 'client': 'Client', 'address': 'Adresse', 'start_date': 'Date de début', 'target_end_date': 'Échéance cible', 'budget': 'Estimation du budget', 'manager': 'Manager'}
class SurveyForm(forms.ModelForm):
    photo_files = MultipleFileField(label='Photos du site', required=False, widget=MultipleFileInput(attrs={'accept': 'image/*'}))
    class Meta:
        model = Survey; fields = ['visit_date', 'findings', 'technical_notes', 'is_validated']
        widgets = {'visit_date': DateInput()}
        labels = {'visit_date': 'Date de la visite', 'findings': 'Constats', 'technical_notes': 'Notes techniques', 'is_validated': 'Validé ?'}
class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote; fields = ['number', 'validity_date', 'status', 'notes']
        widgets = {'validity_date': DateInput()}
        labels = {'number': 'Numéro de devis', 'validity_date': 'Date de validité', 'status': 'Statut', 'notes': 'Notes'}
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase; fields = ['reference', 'supplier', 'description', 'amount', 'status', 'ordered_on', 'delivered_on']
        widgets = {'ordered_on': DateInput(), 'delivered_on': DateInput()}
        labels = {'reference': 'Référence', 'supplier': 'Fournisseur', 'description': 'Description', 'amount': 'Montant', 'status': 'Statut', 'ordered_on': 'Date de commande', 'delivered_on': 'Date de livraison'}
class SiteForm(forms.ModelForm):
    class Meta:
        model = Site; fields = ['supervisor_name', 'progress', 'status', 'started_on', 'completed_on', 'notes']
        widgets = {'started_on': DateInput(), 'completed_on': DateInput()}
        labels = {'supervisor_name': 'Superviseur', 'progress': 'Avancement (%)', 'status': 'Statut', 'started_on': 'Date de début', 'completed_on': 'Date de fin', 'notes': 'Notes'}
class ClosureReportForm(forms.ModelForm):
    photo_files = MultipleFileField(label='Photos du résultat final', required=False, widget=MultipleFileInput(attrs={'accept': 'image/*'}))
    class Meta:
        model = ClosureReport; fields = ['summary', 'lessons_learned', 'final_cost', 'delivered_on']
        widgets = {'delivered_on': DateInput()}
        labels = {'summary': 'Résumé', 'lessons_learned': 'Leçons apprises', 'final_cost': 'Coût final', 'delivered_on': 'Date de livraison'}
