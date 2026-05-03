from django.db import models
from ville.models import Ville

class Hotel(models.Model):
    adresse = models.CharField(max_length=255)
    num_bankily = models.CharField(max_length=20, blank=True, null=True)
    ville = models.ForeignKey(Ville, on_delete=models.PROTECT, related_name='hotels')
    nom = models.CharField(max_length=200, default='Hotel')
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)

    class Meta:
        verbose_name = "Hôtel"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} - {self.ville}"
