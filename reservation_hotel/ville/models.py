from django.db import models

class Ville(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Ville"
        ordering = ['nom']

    def __str__(self):
        return self.nom
