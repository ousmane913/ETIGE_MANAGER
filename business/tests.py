from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User, Group
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase, Client as TestClient

from business.models import (
    Project, Quote, QuoteLine, Purchase, Site, ClosureReport,
    ProjectSchedule, PlanningTask, generate_next_project_number, Client,
)
from business.permissions import ROLE_DG, ROLE_DT, ROLE_EMPLOYEE


class EtigeWorkflowTests(TestCase):
    def setUp(self):
        self.dg_group, _ = Group.objects.get_or_create(name=ROLE_DG)
        self.dt_group, _ = Group.objects.get_or_create(name=ROLE_DT)
        self.employee_group, _ = Group.objects.get_or_create(name=ROLE_EMPLOYEE)

        self.dg_user = User.objects.create_user(username='dg_user', password='password123')
        self.dg_user.groups.add(self.dg_group)

        self.dt_user = User.objects.create_user(username='dt_user', password='password123')
        self.dt_user.groups.add(self.dt_group)

        self.employee_user = User.objects.create_user(username='employee_user', password='password123')
        self.employee_user.groups.add(self.employee_group)

        self.standard_user = User.objects.create_user(username='standard_user', password='password123')

        self.client_entity = Client.objects.create(
            company_name='Client Test SARL',
            contact_name='M. Dupont',
            email='dupont@clienttest.ci',
            phone='+22501020304',
            address='Abidjan Plateau'
        )

    def _project(self, reference, name, **kwargs):
        return Project.objects.create(
            reference=reference,
            name=name,
            client=self.client_entity,
            address='Abidjan',
            **kwargs,
        )

    def test_auto_increment_project_number(self):
        p1 = self._project('REF-001', 'Projet Alpha')
        self.assertTrue(p1.project_number.startswith('PRJ-'))

        p2 = self._project('REF-002', 'Projet Beta')
        self.assertTrue(p2.project_number.startswith('PRJ-'))
        self.assertNotEqual(p1.project_number, p2.project_number)

        next_num = generate_next_project_number()
        self.assertTrue(next_num.startswith('PRJ-'))
        self.assertNotEqual(next_num, p1.project_number)
        self.assertNotEqual(next_num, p2.project_number)

    def test_project_is_linked_to_client(self):
        project = self._project('REF-LINK', 'Projet lié')
        self.assertEqual(project.client_id, self.client_entity.id)
        self.assertEqual(project.client_name, 'Client Test SARL')
        self.assertEqual(project.client_email, 'dupont@clienttest.ci')

        self.client_entity.company_name = 'Client Test SARL (MAJ)'
        self.client_entity.save()
        project.refresh_from_db()
        self.assertEqual(project.client_name, 'Client Test SARL (MAJ)')

    def test_quote_without_survey_allowed(self):
        project = self._project('REF-NOSURVEY', 'Projet Direct')
        quote = Quote(project=project, number=project.project_number, amount_excl_tax=Decimal('150000'), status=Quote.Status.ACCEPTED)
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

    def test_full_workflow_quote_purchase_site_closure(self):
        project = self._project('REF-FLOW', 'Projet workflow')

        purchase = Purchase(
            project=project,
            reference='ACH-001',
            supplier='Fournisseur',
            description='Matériaux',
            amount=Decimal('100000'),
        )
        with self.assertRaises(ValidationError):
            purchase.full_clean()

        Quote.objects.create(project=project, number='DEV-FLOW', amount_excl_tax=Decimal('100000'), status=Quote.Status.ACCEPTED)
        purchase.full_clean()
        purchase.save()

        site = Site(project=project, progress=10)
        with self.assertRaises(ValidationError):
            site.full_clean()

        purchase.status = Purchase.Status.RECEIVED
        purchase.save()
        site.full_clean()
        site.save()
        self.assertEqual(site.status, Site.Status.IN_PROGRESS)

        report = ClosureReport(project=project, summary='Livraison', delivered_on=date.today())
        with self.assertRaises(ValidationError):
            report.full_clean()

        site.progress = 100
        site.full_clean()
        site.save()
        self.assertEqual(site.status, Site.Status.COMPLETED)

        report.full_clean()
        report.save()
        project.status = Project.Status.CLOSED
        project.save()
        self.assertEqual(project.status, Project.Status.CLOSED)

    def test_rejected_quote_blocks_purchase(self):
        project = self._project('REF-REJ', 'Projet refusé')
        Quote.objects.create(project=project, number='DEV-REJ', status=Quote.Status.REJECTED)
        purchase = Purchase(
            project=project,
            reference='ACH-REJ',
            supplier='Fournisseur',
            description='Matériaux',
            amount=Decimal('1000'),
        )
        with self.assertRaises(ValidationError):
            purchase.full_clean()

    def test_planning_creation_and_tasks(self):
        project = self._project('REF-PLAN', 'Projet Planning')
        schedule = ProjectSchedule.objects.create(project=project, notes='Planning initial')
        PlanningTask.objects.create(
            schedule=schedule,
            name='Installation de chantier',
            assigned_to='Ingénieur Travaux',
            status='IN_PROGRESS'
        )
        PlanningTask.objects.create(
            schedule=schedule,
            name='Gros œuvre',
            assigned_to='Chef de chantier',
            status='TODO'
        )
        self.assertEqual(schedule.tasks.count(), 2)

        c = TestClient()
        c.login(username='dg_user', password='password123')
        pdf_resp = c.get(f'/projets/{project.id}/planning/pdf/')
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp['Content-Type'], 'application/pdf')
        self.assertIn('planning-', pdf_resp['Content-Disposition'])

    def test_quote_send_email_uses_client_record(self):
        project = self._project('REF-EMAIL', 'Projet Email')
        quote = Quote.objects.create(project=project, number='DEV-001', amount_excl_tax=Decimal('50000'), status=Quote.Status.ACCEPTED)
        QuoteLine.objects.create(quote=quote, quantity=2, unit='ens', designation='Kit outillage', unit_price=Decimal('25000'))

        c = TestClient()
        c.login(username='dg_user', password='password123')

        response = c.post(f'/projets/{project.id}/devis/{quote.id}/envoyer-email/', {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['dupont@clienttest.ci'])
        self.assertIn('DEV-001', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].attachments[0][0], 'devis-DEV-001.pdf')

        quote.refresh_from_db()
        self.assertEqual(quote.status, Quote.Status.SENT)

    def test_dg_vs_dt_permissions(self):
        project = self._project('REF-ROLES', 'Projet Rôles', budget=Decimal('1000000'))

        c_dt = TestClient()
        c_dt.login(username='dt_user', password='password123')
        self.assertEqual(c_dt.get(f'/projets/{project.id}/').status_code, 200)
        self.assertEqual(c_dt.get(f'/projets/{project.id}/modifier/').status_code, 302)
        self.assertEqual(c_dt.post(f'/projets/{project.id}/supprimer/').status_code, 302)
        self.assertTrue(Project.objects.filter(pk=project.id).exists())

        c_dg = TestClient()
        c_dg.login(username='dg_user', password='password123')
        self.assertEqual(c_dg.get(f'/projets/{project.id}/modifier/').status_code, 200)

    def test_employee_cannot_delete_client_or_project(self):
        project = self._project('REF-EMP', 'Projet employé')
        c = TestClient()
        c.login(username='employee_user', password='password123')

        self.assertEqual(c.get(f'/projets/{project.id}/modifier/').status_code, 302)
        self.assertEqual(c.post(f'/projets/{project.id}/supprimer/').status_code, 302)
        self.assertTrue(Project.objects.filter(pk=project.id).exists())
        self.assertEqual(c.post(f'/clients/{self.client_entity.id}/supprimer/').status_code, 302)
        self.assertTrue(Client.objects.filter(pk=self.client_entity.id).exists())
