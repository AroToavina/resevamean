from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hotel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TypeChambre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100)),
                ('prix_nuit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('capacite', models.PositiveIntegerField(help_text='Nombre maximum de personnes')),
                ('image', models.ImageField(blank=True, null=True, upload_to='types_chambres/')),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Type de Chambre',
            },
        ),
        migrations.CreateModel(
            name='TypeChambreEquipement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chambre.equipement')),
                ('type_chambre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chambre.typechambre')),
            ],
            options={
                'unique_together': {('type_chambre', 'equipement')},
            },
        ),
        migrations.AddField(
            model_name='typechambre',
            name='equipements',
            field=models.ManyToManyField(blank=True, through='chambre.TypeChambreEquipement', to='chambre.equipement'),
        ),
        migrations.CreateModel(
            name='Chambre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20)),
                ('etage', models.PositiveIntegerField(default=0)),
                ('etat', models.CharField(
                    choices=[
                        ('disponible', 'Disponible'),
                        ('reservee', 'Réservée'),
                        ('maintenance', 'En maintenance'),
                        ('hors_service', 'Hors service'),
                    ],
                    default='disponible',
                    max_length=20,
                )),
                ('image', models.ImageField(blank=True, null=True, upload_to='chambres/')),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chambres', to='hotel.hotel')),
                ('type_chambre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chambres', to='chambre.typechambre')),
            ],
            options={
                'verbose_name': 'Chambre',
                'ordering': ['etage', 'numero'],
                'unique_together': {('numero', 'hotel')},
            },
        ),
    ]
