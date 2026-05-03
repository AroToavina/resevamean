from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('utilisateurs/', views.user_list, name='list'),
    path('utilisateurs/creer/', views.user_create, name='create'),
    path('utilisateurs/<int:pk>/modifier/', views.user_edit, name='edit'),
    path('utilisateurs/<int:pk>/statut/', views.user_toggle_status, name='toggle_status'),
    path('historique/', views.historique_list, name='historique'),
    path('statistiques/', views.statistiques, name='statistiques'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/<int:pk>/modifier/', views.client_edit, name='client_edit'),
]
