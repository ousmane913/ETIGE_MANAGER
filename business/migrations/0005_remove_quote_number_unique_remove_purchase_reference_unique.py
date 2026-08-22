from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0004_purchase_delivered_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='number',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='reference',
            field=models.CharField(max_length=40),
        ),
    ]