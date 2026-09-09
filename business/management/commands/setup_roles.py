from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from business.permissions import ROLES


class Command(BaseCommand):
    help = 'Crée les rôles standards ETIGE Manager.'

    def handle(self, *args, **options):
        for role in ROLES:
            Group.objects.get_or_create(name=role)
        self.stdout.write(self.style.SUCCESS('Rôles créés : ' + ', '.join(ROLES)))
