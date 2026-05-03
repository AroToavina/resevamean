from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password


class Client(models.Model):
    TYPE_IDENTITE_CHOICES = [
        ('CNI', 'Carte Nationale d\'Identité'),
        ('PASSEPORT', 'Passeport'),
        ('PERMIS', 'Permis de conduire'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    nationalite = models.CharField(max_length=100)
    type_identite = models.CharField(max_length=20, choices=TYPE_IDENTITE_CHOICES)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    hash_mdp = models.CharField(max_length=255)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def set_password(self, password):
        self.hash_mdp = make_password(password)

    def check_password(self, password):
        return django_check_password(password, self.hash_mdp)
