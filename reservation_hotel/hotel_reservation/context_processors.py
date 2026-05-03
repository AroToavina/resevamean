def current_user_processor(request):
    """Make current_user and current_client available in all templates."""
    return {
        'current_user': getattr(request, 'current_user', None),
        'current_client': getattr(request, 'current_client', None),
    }


def notifications_processor(request):
    """
    Inject reservation expiry notifications on every staff page.
    Filtered by hotel so each staff only sees alerts for their hotel.
    """
    user = getattr(request, 'current_user', None)
    if not user:
        return {}

    try:
        from django.utils import timezone
        import datetime
        from reservation.models import Reservation

        now = timezone.localtime(timezone.now())
        today = now.date()
        demain = today + datetime.timedelta(days=1)
        apres_demain = today + datetime.timedelta(days=2)
        dans_2h = now + datetime.timedelta(hours=2)

        if user.role == 'admin':
            qs = Reservation.objects.all()
        elif user.hotel_id:
            qs = Reservation.objects.filter(chambre__hotel_id=user.hotel_id)
        else:
            return {}

        qs = qs.select_related('client', 'chambre', 'chambre__hotel')

        # Expirees: date_depart passée, pas encore checkout
        notif_expirees = list(qs.filter(
            date_depart__lt=now,
            statut__in=['checkin', 'confirmee']
        ).order_by('date_depart'))

        # Départ aujourd'hui ou arrivée aujourd'hui (en cours)
        notif_auj = list(qs.filter(
            statut__in=['checkin', 'confirmee'],
            date_depart__date=today,
            date_depart__gte=now,
        ))

        # Départ demain
        notif_demain = list(qs.filter(
            date_depart__date=demain,
            statut__in=['checkin', 'confirmee']
        ))

        # Départ dans 2 jours
        notif_J2 = list(qs.filter(
            date_depart__date=apres_demain,
            statut__in=['checkin', 'confirmee']
        ))

        # ALERTE: se termine dans moins de 2h (en checkin)
        notif_bientot = list(qs.filter(
            statut='checkin',
            date_depart__gt=now,
            date_depart__lte=dans_2h,
        ))

        total_alertes = len(notif_expirees) + len(notif_auj) + len(notif_demain) + len(notif_bientot)

        return {
            'notif_expirees': notif_expirees,
            'notif_auj': notif_auj,
            'notif_demain': notif_demain,
            'notif_J2': notif_J2,
            'notif_bientot': notif_bientot,
            'total_alertes': total_alertes,
            'notif_today': today,
            'notif_demain_date': demain,
            'notif_J2_date': apres_demain,
        }
    except Exception:
        return {}
