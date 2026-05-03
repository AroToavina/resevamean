from django.urls import path
from . import views

app_name = 'chambre'

urlpatterns = [
    path('', views.chambre_list, name='list'),
    path('creer/', views.chambre_create, name='create'),
    path('<int:pk>/modifier/', views.chambre_edit, name='edit'),
    path('<int:pk>/supprimer/', views.chambre_delete, name='delete'),
    path('types/', views.type_list, name='type_list'),
    path('types/creer/', views.type_create, name='type_create'),
    path('types/<int:pk>/modifier/', views.type_edit, name='type_edit'),
    path('types/<int:pk>/supprimer/', views.type_delete, name='type_delete'),
    path('equipements/', views.equipement_list, name='equipement_list'),
]
