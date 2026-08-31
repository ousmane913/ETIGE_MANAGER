import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Initialise les rôles (groupes) de l'application"

    def handle(self, *args, **options):
        roles = ['Employé', 'Manager', 'DT', 'DG']
        for role_name in roles:
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Groupe créé : {role_name}"))
            else:
                self.stdout.write(f"Le groupe {role_name} existe déjà.")
        self.stdout.write(self.style.SUCCESS("Initialisation des rôles terminée avec succès."))
