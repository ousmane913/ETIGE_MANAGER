from django.contrib import admin
from .models import Client, Project, Survey, Quote, Purchase, Site, ClosureReport
admin.site.register([Client, Project, Survey, Quote, Purchase, Site, ClosureReport])
