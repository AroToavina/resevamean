from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    path('', views.home, name='home'),
    path('recherche/', views.recherche_chambres, name='recherche'),
    path('reserver/', views.reserver, name='reserver'),
    path('paiement/', views.paiement_reservation, name='paiement_reservation'),
    path('paiement/bankily/soumettre/', views.soumettre_bankily, name='soumettre_bankily'),
    path('confirmation/', views.confirmation_reservation, name='confirmation_reservation'),
    path('login/', views.client_login, name='login'),
    path('logout/', views.client_logout, name='logout'),
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('mes-reservations/<str:token>/', views.detail_reservation, name='detail_reservation'),
    path('mes-reservations/<str:token>/annuler/', views.annuler_reservation, name='annuler_reservation'),
    path('mes-reservations/<str:resa_token>/evaluer/<int:service_id>/', views.evaluer_service, name='evaluer_service'),
]
