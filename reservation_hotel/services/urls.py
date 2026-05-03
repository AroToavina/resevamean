from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('creer/', views.service_create, name='create'),
    path('<int:pk>/modifier/', views.service_edit, name='edit'),
    path('<int:pk>/supprimer/', views.service_delete, name='delete'),
]
