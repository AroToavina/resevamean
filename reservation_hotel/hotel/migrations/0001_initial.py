from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ville', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adresse', models.CharField(max_length=255)),
                ('num_bankily', models.CharField(blank=True, max_length=20, null=True)),
                ('nom', models.CharField(default='Hotel', max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('telephone', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='hotels/')),
                ('ville', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hotels', to='ville.ville')),
            ],
            options={
                'verbose_name': 'Hôtel',
                'ordering': ['nom'],
            },
        ),
    ]
