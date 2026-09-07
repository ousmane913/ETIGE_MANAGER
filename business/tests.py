from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.core import mail
from django.test import TestCase, Client as TestClient
from business.models import Project, Quote, QuoteLine, ProjectSchedule, PlanningTask, generate_next_project_number, Client

class EtigeWorkflowTests(TestCase):
    def setUp(self):
        self.dg_group, _ = Group.objects.get_or_create(name='DG')
        self.dt_group, _ = Group.objects.get_or_create(name='DT')

        self.dg_user = User.objects.create_user(username='dg_user', password='password123')
        self.dg_user.groups.add(self.dg_group)

        self.dt_user = User.objects.create_user(username='dt_user', password='password123')
        self.dt_user.groups.add(self.dt_group)

        self.standard_user = User.objects.create_user(username='standard_user', password='password123')

        self.client_entity = Client.objects.create(
            company_name='Client Test SARL',
            contact_name='M. Dupont',
            email='dupont@clienttest.ci',
            phone='+22501020304',
            address='Abidjan Plateau'
        )

    def test_auto_increment_project_number(self):
        """Vérifie que le numéro de projet ETIGE s'auto-incrémente correctement."""
        p1 = Project.objects.create(reference='REF-001', name='Projet Alpha', client='Client Test SARL')
        self.assertTrue(p1.project_number.startswith('PRJ-'))

        p2 = Project.objects.create(reference='REF-002', name='Projet Beta', client='Client Test SARL')
        self.assertTrue(p2.project_number.startswith('PRJ-'))
        self.assertNotEqual(p1.project_number, p2.project_number)

        next_num = generate_next_project_number()
        self.assertTrue(next_num.startswith('PRJ-'))

    def test_quote_without_survey_allowed(self):
        """Vérifie qu'un devis peut être créé sans qu'un survey ne soit créé ou obligatoire."""
        project = Project.objects.create(reference='REF-NOSURVEY', name='Projet Direct', client='Client Test SARL')
        # Pas de survey créé sur ce projet
        quote = Quote(project=project, number=project.project_number, amount_excl_tax=Decimal('150000'))
        # Doit passer sans ValidationError
        quote.full_clean()
        quote.save()

        line = QuoteLine(
            quote=quote,
            quantity=10,
            unit='m²',
            designation='Pose de carrelage',
            unit_price=Decimal('15000')
        )
        line.full_clean()
        line.save()

        self.assertEqual(line.unit, 'm²')
        self.assertEqual(line.amount, Decimal('150000'))

    def test_planning_creation_and_tasks(self):
        """Vérifie la création d'un planning avec ses phases/tâches."""
        project = Project.objects.create(reference='REF-PLAN', name='Projet Planning', client='Client Test SARL')
        schedule = ProjectSchedule.objects.create(
            project=project,
            notes='Planning initial'
        )
        t1 = PlanningTask.objects.create(
            schedule=schedule,
            name='Installation de chantier',
            assigned_to='Ingénieur Travaux',
            status='IN_PROGRESS'
        )
        t2 = PlanningTask.objects.create(
            schedule=schedule,
            name='Gros œuvre',
            assigned_to='Chef de chantier',
            status='TODO'
        )
        self.assertEqual(schedule.tasks.count(), 2)
        self.assertEqual(t1.status, 'IN_PROGRESS')

        # Test génération et téléchargement PDF du planning pour le client
        c = TestClient()
        c.login(username='dg_user', password='password123')
        pdf_resp = c.get(f'/projets/{project.id}/planning/pdf/')
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp['Content-Type'], 'application/pdf')
        self.assertIn('planning-', pdf_resp['Content-Disposition'])

    def test_quote_send_email(self):
        """Vérifie l'envoi du devis en pièce jointe PDF par email au client."""
        project = Project.objects.create(reference='REF-EMAIL', name='Projet Email', client='Client Test SARL')
        quote = Quote.objects.create(project=project, number='DEV-001', amount_excl_tax=Decimal('50000'))
        QuoteLine.objects.create(quote=quote, quantity=2, unit='ens', designation='Kit outillage', unit_price=Decimal('25000'))

        c = TestClient()
        c.login(username='dg_user', password='password123')

        response = c.post(f'/projets/{project.id}/devis/envoyer-email/', {'email': 'dupont@clienttest.ci'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ['dupont@clienttest.ci'])
        self.assertIn('DEV-001', sent_email.subject)
        self.assertEqual(len(sent_email.attachments), 1)
        self.assertEqual(sent_email.attachments[0][0], 'devis-DEV-001.pdf')

        quote.refresh_from_db()
        self.assertEqual(quote.status, Quote.Status.SENT)

    def test_dg_vs_dt_permissions(self):
        """Vérifie que DT a accès en lecture aux données financières et que DG seul peut modifier/supprimer le projet."""
        project = Project.objects.create(reference='REF-ROLES', name='Projet Rôles', client='Client Test SARL', budget=Decimal('1000000'))

        c_dt = TestClient()
        c_dt.login(username='dt_user', password='password123')

        # DT consulte le projet -> 200 OK
        resp_dt = c_dt.get(f'/projets/{project.id}/')
        self.assertEqual(resp_dt.status_code, 200)

        # DT tente de modifier le projet -> refusé et redirigé
        resp_dt_edit = c_dt.get(f'/projets/{project.id}/modifier/')
        self.assertEqual(resp_dt_edit.status_code, 302)

        # DG tente de modifier le projet -> autorisé (200 OK)
        c_dg = TestClient()
        c_dg.login(username='dg_user', password='password123')
        resp_dg_edit = c_dg.get(f'/projets/{project.id}/modifier/')
        self.assertEqual(resp_dg_edit.status_code, 200)
