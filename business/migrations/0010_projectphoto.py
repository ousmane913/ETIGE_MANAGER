from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('business', '0009_quote_amount_excl_tax_default')]
    operations = [migrations.CreateModel(name='ProjectPhoto', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('created_at', models.DateTimeField(auto_now_add=True)),
        ('updated_at', models.DateTimeField(auto_now=True)),
        ('category', models.CharField(choices=[('SURVEY', 'Survey'), ('CLOSURE', 'Clôture')], max_length=12)),
        ('image', models.ImageField(upload_to='projects/photos/')),
        ('caption', models.CharField(blank=True, max_length=180)),
        ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='business.project')),
    ])]