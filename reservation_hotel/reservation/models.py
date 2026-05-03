from django.db import models
from django.utils import timezone
from client.models import Client
from chambre.models import Chambre
from services.models import Service


class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('confirmee', 'Confirmée'),
        ('checkin', 'Check-in effectué'),
        ('checkout', 'Check-out effectué'),
        ('annulee', 'Annulée'),
    ]

    date_arrivee = models.DateTimeField()
    date_depart = models.DateTimeField()
    nbr_adultes = models.PositiveIntegerField(default=1)
    nbr_enfants = models.PositiveIntegerField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='reservations')
    chambre = models.ForeignKey(Chambre, on_delete=models.PROTECT, related_name='reservations')
    user_confirme = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations_confirmees'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    montant_rembourse = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Réservation"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Résa #{self.pk} - {self.client} - {self.chambre}"

    @property
    def nombre_nuits(self):
        import math
        # Durée en heures divisée par 24
        delta = self.date_depart - self.date_arrivee
        nuits = math.ceil(delta.total_seconds() / 86400)
        return max(nuits, 1)

    @property
    def montant_chambre(self):
        return self.chambre.type_chambre.prix_nuit * self.nombre_nuits

    @property
    def montant_services(self):
        return sum(rs.total for rs in self.reservation_services.all())

    @property
    def montant_total(self):
        return self.montant_chambre + self.montant_services

    @property
    def montant_paye(self):
        # Somme des paiements normaux moins remboursements
        payes = sum(p.montant_paye for p in self.paiements.filter(status='confirme', est_remboursement=False))
        rembourses = sum(p.montant_paye for p in self.paiements.filter(status='confirme', est_remboursement=True))
        return payes - rembourses

    @property
    def montant_restant(self):
        return max(self.montant_total - self.montant_paye, 0)

    @property
    def est_bientot_terminee(self):
        """Retourne True si la réservation se termine dans moins de 2h."""
        from django.utils import timezone
        import datetime
        if self.statut != 'checkin':
            return False
        now = timezone.localtime(timezone.now())
        delta = self.date_depart - now
        return datetime.timedelta(0) < delta <= datetime.timedelta(hours=2)

    def total_personnes(self):
        return self.nbr_adultes + self.nbr_enfants


class ReservationService(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='reservation_services')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    date_consommation = models.DateField()
    user_ajoute = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Service de réservation"

    def __str__(self):
        return f"{self.service.nom_service} x{self.quantite}"

    @property
    def total(self):
        return self.service.prix * self.quantite


class HistoriqueReservation(models.Model):
    ACTION_CHOICES = [
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
    ]

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='historique')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    email_user = models.EmailField(blank=True, null=True, help_text="Email de l'utilisateur staff")
    email_client = models.EmailField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Historique"
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.get_action_display()} - Résa #{self.reservation_id}"


class EvaluationService(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='evaluations')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    note = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField(blank=True)
    date_evaluation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reservation', 'service')
        verbose_name = "Évaluation"

    def __str__(self):
        return f"{self.service} - {self.note}/5"
