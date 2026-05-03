from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
import datetime
from users.models import User
from users.decorators import staff_required, role_required
from hotel.models import Hotel
from reservation.models import Reservation, HistoriqueReservation


def login_view(request):
    if request.session.get('staff_id'):
        return redirect('users:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                if not user.statut:
                    messages.error(request, "Votre compte est désactivé. Contactez l'administrateur.")
                    return render(request, 'admin/login.html')
                request.session['staff_id'] = user.pk
                request.session['staff_role'] = user.role
                messages.success(request, f"Bienvenue, {user.prenom} {user.nom}!")
                return redirect('users:dashboard')
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
        except User.DoesNotExist:
            messages.error(request, "Email ou mot de passe incorrect.")

    return render(request, 'admin/login.html')


def logout_view(request):
    if 'staff_id' in request.session:
        del request.session['staff_id']
    if 'staff_role' in request.session:
        del request.session['staff_role']
    messages.success(request, "Déconnexion réussie.")
    return redirect('users:login')


@staff_required
def dashboard(request):
    user = request.current_user
    now = timezone.localtime(timezone.now())
    today = now.date()
    demain = today + datetime.timedelta(days=1)

    # Filtrer par hôtel selon le rôle
    if user.role == 'admin':
        hotels = Hotel.objects.all()
        reservations = Reservation.objects.all()
    else:
        hotels = Hotel.objects.filter(pk=user.hotel_id)
        reservations = Reservation.objects.filter(chambre__hotel=user.hotel)

    stats = {
        'total_reservations': reservations.count(),
        'reservations_encours': reservations.filter(statut='checkin').count(),
        'reservations_attente': reservations.filter(statut='en_attente').count(),
        # Arrivées aujourd'hui : date_arrivee (date part) = today (tous statuts actifs)
        # date_arrivee est un DateTimeField, il faut comparer la partie date seulement.
        # on compte les clients uniques pour éviter de gonfler le chiffre si un même client a plusieurs réservations
        'checkin_today': reservations.filter(
            date_arrivee__date=today,
            statut__in=['en_attente', 'confirmee', 'checkin', 'checkout']
        ).values('client').distinct().count(),
        # Départs aujourd'hui : seulement les checkout réellement effectués aujourd'hui
        # on compare également sur la date pour être sûr de capturer les horaires non nuls.
        'checkout_today': reservations.filter(
            statut='checkout'
        ).filter(
            Q(date_depart__date=today) | Q(date_arrivee__date=today)
        ).count(),
    }

    # ── Notifications d'expiration ─────────────────────────────────────────
    # 1. Déjà expirées : date_depart (date) < today, pas encore checkout
    expirees = reservations.filter(
        date_depart__date__lt=today,
        statut__in=['checkin', 'confirmee']
    ).select_related('client', 'chambre', 'chambre__hotel').order_by('date_depart')

    # 2. Expirent aujourd'hui (départ = aujourd'hui, encore en checkin)
    expirent_auj = reservations.filter(
        date_depart__date=today,
        statut='checkin'
    ).select_related('client', 'chambre', 'chambre__hotel')

    # 3. Expirent demain (pour prévenir à l'avance)
    expirent_demain = reservations.filter(
        date_depart__date=demain,
        statut='checkin'
    ).select_related('client', 'chambre', 'chambre__hotel')

    # context keys should match what the template expects
    context = {
        'stats': stats,
        'hotels': hotels,
        'notif_expirees': expirees,
        'notif_auj': expirent_auj,
        'notif_demain': expirent_demain,
        'recent_reservations': reservations.select_related('client', 'chambre')[:10],
        'today': today,
        'demain': demain,
    }
    return render(request, 'admin/dashboard/dashboard.html', context)


@staff_required
@role_required('admin', 'manager')
def user_list(request):
    user = request.current_user
    if user.role == 'admin':
        users = User.objects.select_related('hotel').all()
    else:
        # Manager: uniquement les users de son hotel, jamais les admins
        users = User.objects.filter(hotel=user.hotel).exclude(role='admin').select_related('hotel')

    # Filtrage
    role_filter = request.GET.get('role', '')
    hotel_filter = request.GET.get('hotel', '')
    search = request.GET.get('q', '')

    if role_filter:
        users = users.filter(role=role_filter)
    if hotel_filter and user.role == 'admin':
        users = users.filter(hotel_id=hotel_filter)
    if search:
        users = users.filter(Q(nom__icontains=search) | Q(prenom__icontains=search) | Q(email__icontains=search))

    hotels = Hotel.objects.all() if user.role == 'admin' else Hotel.objects.filter(pk=user.hotel_id)
    # Filtrer les roles disponibles selon le rôle courant
    if user.role == 'manager':
        role_choices = [(r, l) for r, l in User.ROLE_CHOICES if r not in ('admin',)]
    else:
        role_choices = User.ROLE_CHOICES

    return render(request, 'admin/users/list.html', {
        'users': users,
        'hotels': hotels,
        'role_choices': role_choices,
        'role_filter': role_filter,
        'hotel_filter': hotel_filter,
        'search': search,
    })


@staff_required
@role_required('admin', 'manager')
def user_create(request):
    user = request.current_user
    hotels = Hotel.objects.all() if user.role == 'admin' else Hotel.objects.filter(pk=user.hotel_id)

    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        role = request.POST.get('role', 'receptionniste')
        hotel_id = request.POST.get('hotel')
        password = request.POST.get('password', '')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        elif not password:
            messages.error(request, "Le mot de passe est requis.")
        else:
            # Manager ne peut créer que des rôles inférieurs
            if user.role == 'manager' and role in ['admin', 'manager']:
                messages.error(request, "Vous ne pouvez pas créer un admin ou manager.")
            else:
                new_user = User(nom=nom, prenom=prenom, email=email, telephone=telephone, role=role)
                if user.role == 'admin':
                    new_user.hotel_id = hotel_id or None
                else:
                    new_user.hotel = user.hotel
                new_user.set_password(password)
                new_user.save()
                messages.success(request, f"Utilisateur {prenom} {nom} créé avec succès.")
                return redirect('users:list')

    role_choices = [(r, l) for r, l in User.ROLE_CHOICES if r != 'admin'] if user.role == 'manager' else User.ROLE_CHOICES
    return render(request, 'admin/users/form.html', {
        'hotels': hotels,
        'role_choices': role_choices,
        'action': 'Créer',
    })


@staff_required
@role_required('admin', 'manager')
def user_edit(request, pk):
    user = request.current_user
    target_user = get_object_or_404(User, pk=pk)

    # Vérifier accès
    if user.role != 'admin' and target_user.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('users:list')

    # Manager ne peut pas éditer un admin
    if user.role == 'manager' and target_user.role == 'admin':
        messages.error(request, "Vous ne pouvez pas modifier un administrateur.")
        return redirect('users:list')

    hotels = Hotel.objects.all() if user.role == 'admin' else Hotel.objects.filter(pk=user.hotel_id)
    if user.role == 'manager':
        role_choices = [(r, l) for r, l in User.ROLE_CHOICES if r not in ('admin',)]
    else:
        role_choices = User.ROLE_CHOICES

    if request.method == 'POST':
        target_user.nom = request.POST.get('nom', '').strip()
        target_user.prenom = request.POST.get('prenom', '').strip()
        target_user.telephone = request.POST.get('telephone', '').strip()
        target_user.statut = bool(request.POST.get('statut'))
        new_role = request.POST.get('role', target_user.role)

        if user.role == 'admin':
            target_user.role = new_role
            hotel_id = request.POST.get('hotel')
            target_user.hotel_id = hotel_id or None
        elif user.role == 'manager' and new_role not in ['admin', 'manager']:
            target_user.role = new_role

        password = request.POST.get('password', '')
        if password:
            target_user.set_password(password)

        target_user.save()
        messages.success(request, "Utilisateur modifié avec succès.")
        return redirect('users:list')

    return render(request, 'admin/users/form.html', {
        'target_user': target_user,
        'hotels': hotels,
        'role_choices': role_choices,
        'action': 'Modifier',
    })


@staff_required
@role_required('admin', 'manager')
def user_toggle_status(request, pk):
    user = request.current_user
    target = get_object_or_404(User, pk=pk)
    if user.role != 'admin' and target.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
    else:
        target.statut = not target.statut
        target.save()
        status = "activé" if target.statut else "désactivé"
        messages.success(request, f"Utilisateur {status}.")
    return redirect('users:list')


@staff_required
@role_required('admin')
def historique_list(request):
    historique = HistoriqueReservation.objects.select_related(
        'reservation', 'reservation__client', 'user'
    ).all()

    hotel_filter = request.GET.get('hotel', '')
    action_filter = request.GET.get('action', '')
    search = request.GET.get('q', '')

    if hotel_filter:
        historique = historique.filter(reservation__chambre__hotel_id=hotel_filter)
    if action_filter:
        historique = historique.filter(action=action_filter)
    if search:
        historique = historique.filter(
            Q(email_user__icontains=search) | Q(description__icontains=search)
        )

    return render(request, 'admin/users/historique.html', {
        'historique': historique[:200],
        'hotels': Hotel.objects.all(),
        'action_choices': HistoriqueReservation.ACTION_CHOICES,
        'hotel_filter': hotel_filter,
        'action_filter': action_filter,
        'search': search,
    })


@staff_required
@role_required('admin')
def statistiques(request):
    from django.db.models import Sum, Avg, Count
    from paiement.models import Paiement
    from client.models import Client
    from chambre.models import Chambre

    hotel_filter = request.GET.get('hotel', '')
    hotels = Hotel.objects.all()

    reservations = Reservation.objects.all()
    chambres_qs = Chambre.objects.all()
    if hotel_filter:
        reservations = reservations.filter(chambre__hotel_id=hotel_filter)
        chambres_qs = chambres_qs.filter(hotel_id=hotel_filter)

    total_reservations = reservations.count()
    total_clients = Client.objects.count()
    total_chambres = chambres_qs.count()

    # Revenus : somme des paiements confirmés NON remboursés, moins les remboursements
    total_revenu_brut = Paiement.objects.filter(
        status='confirme',
        est_remboursement=False,
        reservation__in=reservations
    ).aggregate(s=Sum('montant_paye'))['s'] or 0

    total_rembourse = Paiement.objects.filter(
        status='confirme',
        est_remboursement=True,
        reservation__in=reservations
    ).aggregate(s=Sum('montant_paye'))['s'] or 0

    total_revenu = total_revenu_brut - total_rembourse

    # Stats par mois (12 derniers mois)
    import calendar
    today = timezone.now().date()
    stats_mois = []
    for i in range(11, -1, -1):
        month = (today.month - i - 1) % 12 + 1
        year = today.year - ((today.month - i - 1) // 12 + (1 if (today.month - i - 1) < 0 else 0))
        if today.month - i <= 0:
            year = today.year - 1
            month = today.month - i + 12
        else:
            year = today.year
            month = today.month - i
        # simpler calc
        import datetime
        d = datetime.date(today.year, today.month, 1)
        # Go back i months
        for _ in range(i):
            d = (d.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        count = reservations.filter(date_creation__year=d.year, date_creation__month=d.month).count()
        stats_mois.append({'mois': d.strftime('%b %Y'), 'count': count, 'annee': d.year, 'num': d.month})

    # Répartition par statut
    statuts = []
    for code, label in Reservation.STATUT_CHOICES:
        cnt = reservations.filter(statut=code).count()
        statuts.append({'code': code, 'label': label, 'count': cnt})

    # Taux d'occupation par hôtel
    hotels_all = Hotel.objects.all() if not hotel_filter else Hotel.objects.filter(pk=hotel_filter)
    taux_occupation = []
    for h in hotels_all:
        nb_chambres = h.chambres.count()
        nb_checkin = Reservation.objects.filter(chambre__hotel=h, statut='checkin').count()
        taux = round((nb_checkin / nb_chambres * 100) if nb_chambres > 0 else 0)
        taux_occupation.append({'hotel': h, 'taux': taux, 'nb_chambres': nb_chambres})

    # Revenus par hôtel
    revenus_hotels = []
    if not hotel_filter:
        for h in hotels_all:
            nb = Reservation.objects.filter(chambre__hotel=h).count()
            rev_brut = Paiement.objects.filter(
                status='confirme', est_remboursement=False, reservation__chambre__hotel=h
            ).aggregate(s=Sum('montant_paye'))['s'] or 0
            rev_remb = Paiement.objects.filter(
                status='confirme', est_remboursement=True, reservation__chambre__hotel=h
            ).aggregate(s=Sum('montant_paye'))['s'] or 0
            rev = rev_brut - rev_remb
            revenus_hotels.append({'hotel': h, 'nb_reservations': nb, 'revenu': rev})

    return render(request, 'admin/statistiques/dashboard.html', {
        'hotels': hotels,
        'hotel_filter': hotel_filter,
        'total_reservations': total_reservations,
        'total_revenu': total_revenu,
        'total_clients': total_clients,
        'total_chambres': total_chambres,
        'stats_mois': stats_mois,
        'statuts': statuts,
        'stats_statuts': statuts,
        'taux_occupation': taux_occupation,
        'revenus_hotels': revenus_hotels,
    })


@staff_required
@role_required('admin')
def client_list(request):
    from client.models import Client
    search = request.GET.get('q', '')
    clients = Client.objects.all()
    if search:
        from django.db.models import Q
        clients = clients.filter(
            Q(nom__icontains=search) | Q(prenom__icontains=search) |
            Q(email__icontains=search) | Q(telephone__icontains=search)
        )
    return render(request, 'admin/users/client_list.html', {
        'clients': clients.order_by('-date_inscription')[:200],
        'search': search,
    })


@staff_required
@role_required('admin')
def client_edit(request, pk):
    from client.models import Client
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.nom = request.POST.get('nom', client.nom).strip()
        client.prenom = request.POST.get('prenom', client.prenom).strip()
        telephone = request.POST.get('telephone', client.telephone).strip()
        email = request.POST.get('email', client.email).strip()
        # Check email uniqueness
        if Client.objects.filter(email=email).exclude(pk=pk).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre client.")
        else:
            client.telephone = telephone
            client.email = email
            client.nationalite = request.POST.get('nationalite', client.nationalite).strip()
            client.type_identite = request.POST.get('type_identite', client.type_identite)
            client.save()
            messages.success(request, "Client modifié avec succès.")
            return redirect('users:client_list')
    return render(request, 'admin/users/client_edit.html', {'client': client})


@staff_required
def profile(request):
    user = request.current_user
    if request.method == 'POST':
        user.nom = request.POST.get('nom', user.nom).strip()
        user.prenom = request.POST.get('prenom', user.prenom).strip()
        user.telephone = request.POST.get('telephone', user.telephone).strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        if password:
            if password == password_confirm:
                user.set_password(password)
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return render(request, 'admin/users/profile.html', {'user': user})
        user.save()
        messages.success(request, "Profil mis à jour.")
        return redirect('users:profile')
    return render(request, 'admin/users/profile.html', {'user': user})
