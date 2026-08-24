from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0003_alter_closurereport_created_by_alter_project_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='delivered_on',
            field=models.DateField(blank=True, null=True),
        ),
    ]