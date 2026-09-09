import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from business.permissions import ROLES

class Command(BaseCommand):
    help = "Initialise les rôles (groupes) de l'application"

    def handle(self, *args, **options):
        for role_name in ROLES:
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Groupe créé : {role_name}"))
            else:
                self.stdout.write(f"Le groupe {role_name} existe déjà.")
        self.stdout.write(self.style.SUCCESS("Initialisation des rôles terminée avec succès."))
