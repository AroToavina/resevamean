from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_service', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=10)),
                ('categorie', models.CharField(
                    choices=[
                        ('restauration', 'Restauration'),
                        ('spa', 'Spa & Bien-être'),
                        ('transport', 'Transport'),
                        ('blanchisserie', 'Blanchisserie'),
                        ('loisirs', 'Loisirs'),
                        ('autre', 'Autre'),
                    ],
                    default='autre',
                    max_length=20,
                )),
                ('actif', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Service',
                'ordering': ['categorie', 'nom_service'],
            },
        ),
    ]
