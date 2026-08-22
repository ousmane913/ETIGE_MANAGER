from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0006_site_supervisor_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=12)),
                ('designation', models.CharField(max_length=255)),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('quote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='business.quote')),
            ],
        ),
    ]