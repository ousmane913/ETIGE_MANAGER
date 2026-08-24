from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_remove_quote_number_unique_remove_purchase_reference_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='supervisor_name',
            field=models.CharField(blank=True, max_length=120, verbose_name='nom du superviseur'),
        ),
    ]