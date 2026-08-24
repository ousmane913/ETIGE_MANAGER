from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0007_quoteline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quoteline',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]