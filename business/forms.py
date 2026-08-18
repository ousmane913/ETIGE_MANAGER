from django import forms
from .models import Client, Project, Survey, Quote, Purchase, Site, ClosureReport

class DateInput(forms.DateInput): input_type = 'date'
class ClientForm(forms.ModelForm):
    class Meta: model = Client; fields = ['company_name', 'contact_name', 'email', 'phone', 'address']
class ProjectForm(forms.ModelForm):
    class Meta: model = Project; fields = ['reference', 'name', 'client', 'address', 'start_date', 'target_end_date', 'budget', 'manager']; widgets = {'start_date': DateInput(), 'target_end_date': DateInput()}
class SurveyForm(forms.ModelForm):
    class Meta: model = Survey; fields = ['visit_date', 'findings', 'technical_notes', 'is_validated']; widgets = {'visit_date': DateInput()}
class QuoteForm(forms.ModelForm):
    class Meta: model = Quote; fields = ['number', 'amount_excl_tax', 'vat_rate', 'validity_date', 'status', 'notes']; widgets = {'validity_date': DateInput()}
class PurchaseForm(forms.ModelForm):
    class Meta: model = Purchase; fields = ['reference', 'supplier', 'description', 'amount', 'status', 'ordered_on']; widgets = {'ordered_on': DateInput()}
class SiteForm(forms.ModelForm):
    class Meta: model = Site; fields = ['supervisor', 'status', 'progress', 'started_on', 'completed_on', 'notes']; widgets = {'started_on': DateInput(), 'completed_on': DateInput()}
class ClosureReportForm(forms.ModelForm):
    class Meta: model = ClosureReport; fields = ['summary', 'lessons_learned', 'final_cost', 'delivered_on']; widgets = {'delivered_on': DateInput()}
