from django.db import models


class Service(models.Model):
    CATEGORIE_CHOICES = [
        ('restauration', 'Restauration'),
        ('spa', 'Spa & Bien-être'),
        ('transport', 'Transport'),
        ('blanchisserie', 'Blanchisserie'),
        ('loisirs', 'Loisirs'),
        ('autre', 'Autre'),
    ]

    nom_service = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='autre')
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service"
        ordering = ['categorie', 'nom_service']

    def __str__(self):
        return f"{self.nom_service} - {self.prix} MRU"
