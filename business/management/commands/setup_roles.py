from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Crée les rôles standards de BTP Manager.'
    def handle(self, *args, **options):
        for role in ['Administrateur', 'DG', 'Directeur technique', 'Manager', 'Direction', 'Conducteur de travaux', 'Métreur', 'Achats', 'Finance', 'Client']:
            Group.objects.get_or_create(name=role)
        self.stdout.write(self.style.SUCCESS('Rôles créés.'))
