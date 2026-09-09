from django.db import migrations, models
import django.db.models.deletion


def link_projects_to_clients(apps, schema_editor):
    Project = apps.get_model('business', 'Project')
    Client = apps.get_model('business', 'Client')
    ProjectNumberCounter = apps.get_model('business', 'ProjectNumberCounter')
    ProjectNumberCounter.objects.get_or_create(pk=1, defaults={'last_value': 0})

    cache = {}
    for project in Project.objects.all():
        name = (project.client_name or '').strip() or 'Client non renseigné'
        key = name.casefold()
        if key not in cache:
            existing = Client.objects.filter(company_name__iexact=name).first()
            if existing is None:
                existing = Client.objects.create(
                    company_name=name,
                    contact_name='—',
                    phone='—',
                )
            cache[key] = existing
        project.client_id = cache[key].id
        project.save(update_fields=['client'])


def unlink_projects_from_clients(apps, schema_editor):
    Project = apps.get_model('business', 'Project')
    Client = apps.get_model('business', 'Client')
    for project in Project.objects.all():
        client = Client.objects.filter(pk=project.client_id).first()
        project.client_name = client.company_name if client else ''
        project.save(update_fields=['client_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0016_alter_purchase_status_alter_quote_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectNumberCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_value', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'compteur de numéros de projet',
                'verbose_name_plural': 'compteurs de numéros de projet',
            },
        ),
        migrations.RenameField(
            model_name='project',
            old_name='client',
            new_name='client_name',
        ),
        migrations.AddField(
            model_name='project',
            name='client',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='projects',
                to='business.client',
                verbose_name='Client',
            ),
        ),
        migrations.RunPython(link_projects_to_clients, unlink_projects_from_clients),
        migrations.AlterField(
            model_name='project',
            name='client',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='projects',
                to='business.client',
                verbose_name='Client',
            ),
        ),
        migrations.RemoveField(
            model_name='project',
            name='client_name',
        ),
    ]
