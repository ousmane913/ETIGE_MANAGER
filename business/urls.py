from django.urls import path
from . import views
urlpatterns = [
    path('clients/', views.clients, name='clients'),
    path('clients/nouveau/', views.client_create, name='client-create'),
    path('clients/<int:client_id>/modifier/', views.client_edit, name='client-edit'),
    path('clients/<int:client_id>/supprimer/', views.client_delete, name='client-delete'),
    path('projets/', views.projects, name='projects'),
    path('projets/nouveau/', views.project_create, name='project-create'),
    path('projets/<int:project_id>/supprimer/', views.project_delete, name='project-delete'),
    path('projets/<int:project_id>/modifier/', views.project_edit, name='project-edit'),
    path('projets/<int:project_id>/', views.project_detail, name='project-detail'),
    path('projets/<int:project_id>/survey/', views.survey_create, name='survey-create'),
    path('projets/<int:project_id>/devis/', views.quote_create, name='quote-create'),
    path('projets/<int:project_id>/devis/pdf/', views.quote_pdf, name='quote-pdf'),
    path('projets/<int:project_id>/achats/', views.purchase_create, name='purchase-create'),
    path('projets/<int:project_id>/chantier/', views.site_create, name='site-create'),
    path('projets/<int:project_id>/cloture/', views.closure_create, name='closure-create'),
]
