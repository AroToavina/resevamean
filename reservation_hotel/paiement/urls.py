from django.urls import path
from . import views

app_name = 'paiement'

urlpatterns = [
    path('', views.paiement_list, name='list'),
    path('reservation/<int:resa_pk>/ajouter/', views.ajouter_paiement, name='ajouter'),
]
