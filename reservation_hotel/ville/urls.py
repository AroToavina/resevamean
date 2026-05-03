from django.urls import path
from . import views

app_name = 'ville'

urlpatterns = [
    path('', views.ville_list, name='list'),
    path('<int:pk>/supprimer/', views.ville_delete, name='delete'),
]
