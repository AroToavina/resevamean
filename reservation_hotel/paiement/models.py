from django.db import models
from reservation.models import Reservation
from client.models import Client


class Paiement(models.Model):
    MODE_CHOICES = [
        ('bankily', 'Bankily'),
        ('visa', 'Visa/MasterCard'),
        ('espace', 'Espace'),
        ('especes', 'Espèces'),
    ]
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('echec', 'Échec'),
        ('rembourse', 'Remboursé'),
    ]

    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='paiements')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='paiements')
    user = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='paiements_confirmes'
    )
    est_remboursement = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Paiement"
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Paiement {self.montant_paye} MRU - {self.get_mode_display()} ({self.get_status_display()})"


class PaiementBankily(models.Model):
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE, related_name='bankily_detail')
    code_transaction = models.CharField(max_length=100, blank=True)
    numero_bankily = models.CharField(max_length=20, help_text="Numéro Bankily de l'hôtel")
    numero_client = models.CharField(max_length=20, blank=True, help_text="Numéro Bankily du client")
    capture_ecran = models.ImageField(upload_to='paiements/bankily/', blank=True, null=True)
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bankily - {self.numero_bankily}"


class PaiementVisa(models.Model):
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE, related_name='visa_detail')
    numero_carte = models.CharField(max_length=19)
    titulaire = models.CharField(max_length=100)
    expiration = models.CharField(max_length=7)
    cvv_hash = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Visa - **** {self.numero_carte[-4:]}"
