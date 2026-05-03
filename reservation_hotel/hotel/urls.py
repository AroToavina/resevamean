from django.urls import path
from . import views

app_name = 'hotel'

urlpatterns = [
    path('', views.hotel_list, name='list'),
    path('creer/', views.hotel_create, name='create'),
    path('<int:pk>/modifier/', views.hotel_edit, name='edit'),
]
