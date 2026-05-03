from django.db import models
from hotel.models import Hotel


class Equipement(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class TypeChambre(models.Model):
    libelle = models.CharField(max_length=100)
    prix_nuit = models.DecimalField(max_digits=10, decimal_places=2)
    capacite = models.PositiveIntegerField(help_text="Nombre maximum de personnes")
    equipements = models.ManyToManyField(Equipement, through='TypeChambreEquipement', blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Type de Chambre"

    def __str__(self):
        return f"{self.libelle} ({self.capacite} pers.) - {self.prix_nuit} MRU/nuit"


class TypeChambreEquipement(models.Model):
    type_chambre = models.ForeignKey(TypeChambre, on_delete=models.CASCADE)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('type_chambre', 'equipement')


class Chambre(models.Model):
    ETAT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservee', 'Réservée'),
        ('maintenance', 'En maintenance'),
        ('hors_service', 'Hors service'),
    ]

    numero = models.CharField(max_length=20)
    etage = models.PositiveIntegerField(default=0)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='disponible')
    image = models.ImageField(upload_to='chambres/', blank=True, null=True)
    type_chambre = models.ForeignKey(TypeChambre, on_delete=models.PROTECT, related_name='chambres')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='chambres')

    class Meta:
        unique_together = ('numero', 'hotel')
        verbose_name = "Chambre"
        ordering = ['etage', 'numero']

    def __str__(self):
        return f"Chambre {self.numero} - Étage {self.etage} ({self.type_chambre.libelle})"

    def is_available_for_dates(self, date_arrivee, date_depart, exclude_resa_id=None):
        from reservation.models import Reservation
        qs = self.reservations.filter(
            statut__in=['en_attente', 'confirmee', 'checkin'],
        ).filter(
            date_arrivee__lt=date_depart,
            date_depart__gt=date_arrivee,
        )
        if exclude_resa_id:
            qs = qs.exclude(id=exclude_resa_id)
        return not qs.exists()
