from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0008_quoteline_quantity_integer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='amount_excl_tax',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=14),
        ),
    ]