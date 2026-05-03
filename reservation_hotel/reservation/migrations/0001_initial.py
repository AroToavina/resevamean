from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chambre', '0001_initial'),
        ('client', '0001_initial'),
        ('services', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_arrivee', models.DateField()),
                ('date_depart', models.DateField()),
                ('nbr_adultes', models.PositiveIntegerField(default=1)),
                ('nbr_enfants', models.PositiveIntegerField(default=0)),
                ('statut', models.CharField(
                    choices=[
                        ('en_attente', 'En attente de paiement'),
                        ('confirmee', 'Confirmée'),
                        ('checkin', 'Check-in effectué'),
                        ('checkout', 'Check-out effectué'),
                        ('annulee', 'Annulée'),
                    ],
                    default='en_attente',
                    max_length=20,
                )),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('montant_rembourse', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('chambre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to='chambre.chambre')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to='client.client')),
                ('user_confirme', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reservations_confirmees',
                    to='users.user',
                )),
            ],
            options={
                'verbose_name': 'Réservation',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.CreateModel(
            name='ReservationService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.PositiveIntegerField(default=1)),
                ('date_consommation', models.DateField()),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservation_services', to='reservation.reservation')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='services.service')),
                ('user_ajoute', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='users.user',
                )),
            ],
            options={
                'verbose_name': 'Service de réservation',
            },
        ),
        migrations.CreateModel(
            name='HistoriqueReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(
                    choices=[
                        ('creation', 'Création'),
                        ('confirmation', 'Confirmation'),
                        ('checkin', 'Check-in'),
                        ('checkout', 'Check-out'),
                        ('annulation', 'Annulation'),
                        ('ajout_service', 'Ajout service'),
                        ('suppression_service', 'Suppression service'),
                        ('paiement', 'Paiement'),
                        ('remboursement', 'Remboursement'),
                        ('modification', 'Modification'),
                    ],
                    max_length=30,
                )),
                ('description', models.TextField()),
                ('email_user', models.EmailField(blank=True, help_text="Email de l'utilisateur staff", max_length=254, null=True)),
                ('email_client', models.EmailField(blank=True, max_length=254, null=True)),
                ('date_action', models.DateTimeField(auto_now_add=True)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historique', to='reservation.reservation')),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='users.user',
                )),
            ],
            options={
                'verbose_name': 'Historique',
                'ordering': ['-date_action'],
            },
        ),
        migrations.CreateModel(
            name='EvaluationService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('commentaire', models.TextField(blank=True)),
                ('date_evaluation', models.DateTimeField(auto_now_add=True)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='reservation.reservation')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.service')),
            ],
            options={
                'verbose_name': 'Évaluation',
                'unique_together': {('reservation', 'service')},
            },
        ),
    ]
