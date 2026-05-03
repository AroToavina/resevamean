from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    path('', views.reservation_list, name='list'),
    path('creer/', views.reservation_create, name='create'),
    path('api/client-lookup/', views.api_client_lookup, name='api_client_lookup'),
    path('api/chambres-disponibles/', views.api_chambres_disponibles, name='api_chambres_disponibles'),
    path('<int:pk>/', views.reservation_detail, name='detail'),
    path('<int:pk>/checkin/', views.checkin, name='checkin'),
    path('<int:pk>/checkout/', views.checkout, name='checkout'),
    path('<int:pk>/annuler/', views.annuler_reservation, name='annuler'),
    path('<int:pk>/service/ajouter/', views.ajouter_service, name='ajouter_service'),
    path('<int:pk>/service/<int:rs_pk>/supprimer/', views.supprimer_service, name='supprimer_service'),
    path('<int:pk>/paiement/<int:paiement_pk>/confirmer-bankily/', views.confirmer_paiement_bankily, name='confirmer_bankily'),
    path('<int:pk>/rembourser/', views.rembourser, name='rembourser'),
    path('<int:pk>/prolonger/', views.prolonger_reservation, name='prolonger'),
]
