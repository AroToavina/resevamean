from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paiement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paiementbankily',
            name='numero_client',
            field=models.CharField(blank=True, help_text='Numéro Bankily du client', max_length=20),
        ),
        migrations.AlterField(
            model_name='paiementbankily',
            name='numero_bankily',
            field=models.CharField(help_text="Numéro Bankily de l'hôtel", max_length=20),
        ),
    ]
