from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0001_initial'),
        ('reservation', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_paye', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_paiement', models.DateTimeField(auto_now_add=True)),
                ('mode', models.CharField(
                    choices=[
                        ('bankily', 'Bankily'),
                        ('visa', 'Visa/MasterCard'),
                        ('espace', 'Espace'),
                        ('especes', 'Espèces'),
                    ],
                    max_length=20,
                )),
                ('status', models.CharField(
                    choices=[
                        ('en_attente', 'En attente'),
                        ('confirme', 'Confirmé'),
                        ('echec', 'Échec'),
                        ('rembourse', 'Remboursé'),
                    ],
                    default='en_attente',
                    max_length=20,
                )),
                ('est_remboursement', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='paiements', to='client.client')),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paiements', to='reservation.reservation')),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='paiements_confirmes',
                    to='users.user',
                )),
            ],
            options={
                'verbose_name': 'Paiement',
                'ordering': ['-date_paiement'],
            },
        ),
        migrations.CreateModel(
            name='PaiementBankily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_transaction', models.CharField(blank=True, max_length=100)),
                ('numero_bankily', models.CharField(max_length=20)),
                ('capture_ecran', models.ImageField(blank=True, null=True, upload_to='paiements/bankily/')),
                ('date_envoi', models.DateTimeField(auto_now_add=True)),
                ('paiement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bankily_detail', to='paiement.paiement')),
            ],
        ),
        migrations.CreateModel(
            name='PaiementVisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_carte', models.CharField(max_length=19)),
                ('titulaire', models.CharField(max_length=100)),
                ('expiration', models.CharField(max_length=7)),
                ('cvv_hash', models.CharField(max_length=255)),
                ('transaction_id', models.CharField(blank=True, max_length=100)),
                ('paiement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='visa_detail', to='paiement.paiement')),
            ],
        ),
    ]
