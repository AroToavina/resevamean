from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('nationalite', models.CharField(max_length=100)),
                ('type_identite', models.CharField(
                    choices=[
                        ('CNI', "Carte Nationale d'Identité"),
                        ('PASSEPORT', 'Passeport'),
                        ('PERMIS', 'Permis de conduire'),
                    ],
                    max_length=20,
                )),
                ('telephone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('hash_mdp', models.CharField(max_length=255)),
                ('date_inscription', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Client',
                'ordering': ['nom', 'prenom'],
            },
        ),
    ]
