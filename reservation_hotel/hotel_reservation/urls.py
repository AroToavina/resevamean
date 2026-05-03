from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/client/', permanent=False)),
    path('client/', include('client.urls')),
    path('staff/', include('users.urls')),
    path('chambres/', include('chambre.urls')),
    path('reservations/', include('reservation.urls')),
    path('paiements/', include('paiement.urls')),
    path('services/', include('services.urls')),
    path('hotels/', include('hotel.urls')),
    path('villes/', include('ville.urls')),
    # Fichiers media (uploads)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # Fichiers static servis en mode insecure (développement avec DEBUG=False)
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT, 'show_indexes': False}),
]

handler404 = 'hotel_reservation.views.custom_404'
handler500 = 'hotel_reservation.views.custom_500'
