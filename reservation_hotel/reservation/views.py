from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from reservation.models import Reservation, ReservationService, HistoriqueReservation
from chambre.models import Chambre
from services.models import Service
from users.decorators import staff_required, role_required
from hotel.models import Hotel
from paiement.models import Paiement, PaiementBankily
import datetime


def log_action(reservation, action, description, user=None, email_user=None, email_client=None):
    HistoriqueReservation.objects.create(
        reservation=reservation,
        action=action,
        description=description,
        user=user,
        email_user=email_user or (user.email if user else None),
        email_client=email_client or reservation.client.email,
    )


@staff_required
def reservation_list(request):
    user = request.current_user
    if user.role == 'admin':
        reservations = Reservation.objects.select_related('client', 'chambre', 'chambre__hotel').all()
        hotels = Hotel.objects.all()
    else:
        reservations = Reservation.objects.filter(
            chambre__hotel=user.hotel
        ).select_related('client', 'chambre', 'chambre__hotel')
        hotels = Hotel.objects.filter(pk=user.hotel_id)

    # Filtres
    statut_filter = request.GET.get('statut', '')
    hotel_filter = request.GET.get('hotel', '')
    search = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if statut_filter:
        reservations = reservations.filter(statut=statut_filter)
    if hotel_filter and user.role == 'admin':
        reservations = reservations.filter(chambre__hotel_id=hotel_filter)
    if search:
        reservations = reservations.filter(
            Q(client__nom__icontains=search) | Q(client__prenom__icontains=search) |
            Q(client__email__icontains=search) | Q(chambre__numero__icontains=search)
        )
    if date_from:
        reservations = reservations.filter(date_arrivee__gte=date_from)
    if date_to:
        reservations = reservations.filter(date_arrivee__lte=date_to)

    # Vérifier réservations expirées et notifier
    now = timezone.now()
    expirees = reservations.filter(
        date_depart__lt=now, statut__in=['checkin', 'confirmee']
    )

    return render(request, 'admin/reservation/list.html', {
        'reservations': reservations.order_by('-date_creation')[:100],
        'statut_choices': Reservation.STATUT_CHOICES,
        'hotels': hotels,
        'statut_filter': statut_filter,
        'hotel_filter': hotel_filter,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'expirees_count': expirees.count(),
    })


@staff_required
def reservation_detail(request, pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    historique = resa.historique.all()
    services_dispo = Service.objects.filter(actif=True)
    paiements = resa.paiements.all()

    # Check if reservation is expired
    now = timezone.localtime(timezone.now())
    est_expiree = (resa.statut in ['checkin', 'confirmee'] and resa.date_depart <= now)

    # Check if reservation ends within 2h
    est_bientot_terminee = resa.est_bientot_terminee

    # Check if room is available for extension (after expiry date)
    peut_prolonger = False
    if est_expiree and resa.statut == 'checkin':
        peut_prolonger = True  # staff can choose new end date

    return render(request, 'admin/reservation/detail.html', {
        'resa': resa,
        'historique': historique,
        'services_dispo': services_dispo,
        'paiements': paiements,
        'est_expiree': est_expiree,
        'est_bientot_terminee': est_bientot_terminee,
        'peut_prolonger': peut_prolonger,
        'today': now.date(),
    })


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def checkin(request, pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if resa.statut != 'confirmee':
        messages.error(request, "Seules les réservations confirmées peuvent être en check-in.")
        return redirect('reservation:detail', pk=pk)

    now = timezone.localtime(timezone.now())

    # Pas encore arrivé
    if resa.date_arrivee > now:
        delta = resa.date_arrivee - now
        heures = int(delta.total_seconds() // 3600)
        messages.error(request,
            f"Check-in impossible : l'arrivée est prévue dans {heures}h, "
            f"le {timezone.localtime(resa.date_arrivee).strftime('%d/%m/%Y à %H:%M')}.")
        return redirect('reservation:detail', pk=pk)

    # Réservation déjà terminée
    if resa.date_depart <= now:
        messages.error(request,
            f"Check-in impossible : la réservation s'est terminée le "
            f"{timezone.localtime(resa.date_depart).strftime('%d/%m/%Y à %H:%M')}.")
        return redirect('reservation:detail', pk=pk)

    # OK : now >= date_arrivee et now < date_depart
    if request.method == 'POST':
        resa.statut = 'checkin'
        resa.save()
        log_action(resa, 'checkin', f"Check-in effectué par {user.email}", user=user)
        messages.success(request, "Check-in effectué avec succès.")
        return redirect('reservation:detail', pk=pk)

    return render(request, 'admin/reservation/confirm_action.html', {
        'resa': resa, 'action': 'Check-in', 'action_url': request.path
    })


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def checkout(request, pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if resa.statut != 'checkin':
        messages.error(request, "Seules les réservations en check-in peuvent être checkées out.")
        return redirect('reservation:detail', pk=pk)

    # Vérifier que tout est payé
    if resa.montant_restant > 0:
        messages.error(request, f"Impossible: {resa.montant_restant} MRU restant à payer avant le check-out.")
        return redirect('reservation:detail', pk=pk)

    if request.method == 'POST':
        resa.statut = 'checkout'
        resa.chambre.etat = 'disponible'
        resa.chambre.save()
        resa.save()
        log_action(resa, 'checkout', f"Check-out effectué par {user.email}", user=user)
        messages.success(request, "Check-out effectué avec succès.")
        return redirect('reservation:detail', pk=pk)

    return render(request, 'admin/reservation/confirm_action.html', {
        'resa': resa, 'action': 'Check-out', 'action_url': request.path,
        'montant_total': resa.montant_total, 'montant_paye': resa.montant_paye,
    })


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def ajouter_service(request, pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if resa.statut != 'checkin':
        messages.error(request, "Services uniquement pour réservations en cours.")
        return redirect('reservation:detail', pk=pk)

    if request.method == 'POST':
        service_id = request.POST.get('service')
        quantite = int(request.POST.get('quantite', 1))
        date_conso = request.POST.get('date_consommation') or timezone.now().date()

        service = get_object_or_404(Service, pk=service_id)
        rs = ReservationService.objects.create(
            reservation=resa,
            service=service,
            quantite=quantite,
            date_consommation=date_conso,
            user_ajoute=user,
        )
        log_action(resa, 'ajout_service',
                   f"Service '{service.nom_service}' x{quantite} ajouté par {user.email}",
                   user=user)
        messages.success(request, f"Service '{service.nom_service}' ajouté.")
        return redirect('reservation:detail', pk=pk)

    messages.error(request, "Méthode non autorisée.")
    return redirect('reservation:detail', pk=pk)


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def supprimer_service(request, pk, rs_pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)
    rs = get_object_or_404(ReservationService, pk=rs_pk, reservation=resa)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if resa.statut != 'checkin':
        messages.error(request, "Impossible de supprimer un service hors check-in.")
        return redirect('reservation:detail', pk=pk)

    if request.method == 'POST':
        nom = rs.service.nom_service
        rs.delete()
        log_action(resa, 'suppression_service', f"Service '{nom}' supprimé par {user.email}", user=user)
        messages.success(request, f"Service '{nom}' supprimé.")
        return redirect('reservation:detail', pk=pk)

    return render(request, 'admin/reservation/confirm_action.html', {
        'resa': resa, 'action': f"Supprimer service {rs.service.nom_service}",
        'action_url': request.path
    })


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def annuler_reservation(request, pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if resa.statut not in ['en_attente', 'confirmee']:
        messages.error(request, "Cette réservation ne peut plus être annulée.")
        return redirect('reservation:detail', pk=pk)

    if request.method == 'POST':
        resa.statut = 'annulee'
        resa.save()
        log_action(resa, 'annulation', f"Réservation annulée par {user.email}", user=user)
        messages.success(request, "Réservation annulée.")
        return redirect('reservation:detail', pk=pk)

    return render(request, 'admin/reservation/confirm_action.html', {
        'resa': resa, 'action': 'Annuler', 'action_url': request.path
    })


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def confirmer_paiement_bankily(request, pk, paiement_pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)
    paiement = get_object_or_404(Paiement, pk=paiement_pk, reservation=resa)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if paiement.mode != 'bankily' or paiement.status not in ['en_attente']:
        messages.error(request, "Paiement non éligible à la confirmation.")
        return redirect('reservation:detail', pk=pk)

    # Récupérer les infos soumises par le client
    try:
        bankily = paiement.bankily_detail
    except PaiementBankily.DoesNotExist:
        bankily = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirmer':
            if not bankily or not bankily.code_transaction:
                messages.error(request, "Le client n'a pas encore soumis sa preuve de paiement.")
                return redirect('reservation:confirmer_bankily', pk=pk, paiement_pk=paiement_pk)

            paiement.status = 'confirme'
            paiement.user = user
            paiement.save()

            # Confirmer réservation si en attente
            if resa.statut == 'en_attente':
                resa.statut = 'confirmee'
                resa.user_confirme = user
                resa.save()

            log_action(resa, 'paiement',
                       f"Paiement Bankily {paiement.montant_paye} MRU confirmé par {user.email}. "
                       f"Code client: {bankily.code_transaction}",
                       user=user)
            messages.success(request, "Paiement Bankily confirmé. Réservation confirmée.")

        elif action == 'rejeter':
            paiement.status = 'echec'
            paiement.save()
            log_action(resa, 'paiement',
                       f"Paiement Bankily rejeté par {user.email}. Code soumis: {bankily.code_transaction if bankily else 'N/A'}",
                       user=user)
            messages.warning(request, "Paiement rejeté. Le client sera notifié.")

        return redirect('reservation:detail', pk=pk)

    return render(request, 'admin/reservation/confirmer_bankily.html', {
        'resa': resa,
        'paiement': paiement,
        'bankily': bankily,
    })


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def rembourser(request, pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if resa.statut != 'annulee':
        messages.error(request, "Remboursement uniquement pour réservations annulées.")
        return redirect('reservation:detail', pk=pk)

    if request.method == 'POST':
        montant = resa.montant_paye
        mode = request.POST.get('mode', 'espace')
        if montant <= 0:
            messages.error(request, "Aucun montant à rembourser.")
            return redirect('reservation:detail', pk=pk)

        Paiement.objects.create(
            montant_paye=montant,
            mode=mode,
            status='confirme',
            reservation=resa,
            client=resa.client,
            user=user,
            est_remboursement=True,
            notes=f"Remboursement pour annulation. Mode: {mode}",
        )
        resa.montant_rembourse = montant
        resa.save()

        log_action(resa, 'remboursement',
                   f"Remboursement {montant} MRU effectué par {user.email}. Mode: {mode}",
                   user=user)
        messages.success(request, f"Remboursement de {montant} MRU enregistré.")
        return redirect('reservation:detail', pk=pk)

    return render(request, 'admin/reservation/rembourser.html', {
        'resa': resa,
        'montant_paye': resa.montant_paye,
    })


@staff_required
def reservation_create(request):
    """Réservation directe depuis l'interface staff (ex: employé)"""
    user = request.current_user
    if user.role == 'admin':
        hotels = Hotel.objects.all()
    else:
        hotels = Hotel.objects.filter(pk=user.hotel_id)

    if request.method == 'POST':
        from client.models import Client
        email = request.POST.get('email', '').strip()
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        nationalite = request.POST.get('nationalite', '').strip()
        type_identite = request.POST.get('type_identite', 'CNI')
        chambre_id = request.POST.get('chambre')
        date_arrivee = request.POST.get('date_arrivee')
        date_depart = request.POST.get('date_depart')
        adultes = int(request.POST.get('nbr_adultes', 1))
        enfants = int(request.POST.get('nbr_enfants', 0))

        try:
            # Support both datetime-local (YYYY-MM-DDTHH:MM) and date formats
            from django.utils import timezone as tz
            def parse_dt(s):
                if 'T' in s:
                    dt = datetime.datetime.fromisoformat(s)
                else:
                    dt = datetime.datetime.fromisoformat(s + 'T12:00')
                # Make timezone-aware
                if dt.tzinfo is None:
                    dt = tz.make_aware(dt)
                return dt
            date_arrivee_dt = parse_dt(date_arrivee)
            date_depart_dt = parse_dt(date_depart)
        except ValueError:
            messages.error(request, "Dates invalides.")
            return render(request, 'admin/reservation/create.html', {'hotels': hotels})

        chambre = get_object_or_404(Chambre, pk=chambre_id)

        if not chambre.is_available_for_dates(date_arrivee_dt, date_depart_dt):
            messages.error(request, "Chambre non disponible pour ces dates.")
            return render(request, 'admin/reservation/create.html', {'hotels': hotels})

        client, created = Client.objects.get_or_create(
            email=email,
            defaults={
                'nom': nom, 'prenom': prenom, 'telephone': telephone,
                'nationalite': nationalite, 'type_identite': type_identite,
                'hash_mdp': ''
            }
        )

        resa = Reservation.objects.create(
            date_arrivee=date_arrivee_dt, date_depart=date_depart_dt,
            nbr_adultes=adultes, nbr_enfants=enfants,
            statut='confirmee', client=client, chambre=chambre,
            user_confirme=user,
        )
        log_action(resa, 'creation', f"Réservation créée par {user.email} (staff)", user=user)
        messages.success(request, f"Réservation #{resa.pk} créée.")
        return redirect('reservation:detail', pk=resa.pk)

    return render(request, 'admin/reservation/create.html', {'hotels': hotels})


@staff_required
def api_client_lookup(request):
    """API JSON : retourne les infos d'un client par email."""
    from django.http import JsonResponse
    from client.models import Client
    email = request.GET.get('email', '').strip().lower()
    if not email:
        return JsonResponse({'found': False})
    try:
        client = Client.objects.get(email__iexact=email)
        return JsonResponse({
            'found': True,
            'nom': client.nom,
            'prenom': client.prenom,
            'telephone': client.telephone,
            'nationalite': client.nationalite,
            'type_identite': client.type_identite,
        })
    except Client.DoesNotExist:
        return JsonResponse({'found': False})


@staff_required
def api_chambres_disponibles(request):
    """API JSON : retourne les chambres disponibles d'un hôtel pour des dates et capacité."""
    from django.http import JsonResponse
    hotel_id = request.GET.get('hotel_id')
    date_arrivee = request.GET.get('date_arrivee')
    date_depart = request.GET.get('date_depart')
    nb_adultes = int(request.GET.get('nb_adultes', 1))
    nb_enfants = int(request.GET.get('nb_enfants', 0))
    total_residents = nb_adultes + nb_enfants

    if not hotel_id:
        return JsonResponse({'chambres': []})

    chambres_qs = Chambre.objects.filter(
        hotel_id=hotel_id,
        etat='disponible'
    ).select_related('type_chambre')

    # Filtrer par capacité :
    # - total <= 4 : chambres dont capacite >= total_residents
    # - total >= 5 : chambres dont capacite = 5 uniquement (capacité max)
    if total_residents >= 5:
        chambres_qs = chambres_qs.filter(type_chambre__capacite=5)
    else:
        chambres_qs = chambres_qs.filter(type_chambre__capacite__gte=total_residents)

    if date_arrivee and date_depart:
        try:
            def parse_dt(s):
                if 'T' in s:
                    dt = datetime.datetime.fromisoformat(s)
                else:
                    dt = datetime.datetime.fromisoformat(s + 'T12:00')
                from django.utils import timezone as tz
                if dt.tzinfo is None:
                    dt = tz.make_aware(dt)
                return dt
            arr = parse_dt(date_arrivee)
            dep = parse_dt(date_depart)
            chambres_qs = [c for c in chambres_qs if c.is_available_for_dates(arr, dep)]
        except ValueError:
            pass

    data = []
    for c in chambres_qs:
        data.append({
            'id': c.pk,
            'label': f"Chambre {c.numero} — {c.type_chambre.libelle} (cap. {c.type_chambre.capacite} pers. · {c.type_chambre.prix_nuit} MRU/nuit) — Étage {c.etage}",
            'prix_nuit': str(c.type_chambre.prix_nuit),
            'capacite': c.type_chambre.capacite,
        })

    return JsonResponse({'chambres': data})


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def prolonger_reservation(request, pk):
    import math
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    now = timezone.localtime(timezone.now())

    if resa.statut not in ['checkin', 'confirmee']:
        messages.error(request, "Prolongation impossible pour ce statut.")
        return redirect('reservation:detail', pk=pk)

    date_depart_locale = timezone.localtime(resa.date_depart)
    date_min_prolongation = date_depart_locale + datetime.timedelta(hours=24)
    prix_nuit = resa.chambre.type_chambre.prix_nuit

    if request.method == 'POST':
        nouvelle_date_depart = request.POST.get('nouvelle_date_depart')
        mode_paiement = request.POST.get('mode_paiement', 'especes')
        try:
            if 'T' in nouvelle_date_depart:
                nouvelle_date_dt = datetime.datetime.fromisoformat(nouvelle_date_depart)
            else:
                nouvelle_date_dt = datetime.datetime.fromisoformat(
                    nouvelle_date_depart + 'T' + date_depart_locale.strftime('%H:%M')
                )
            from django.utils import timezone as tz
            if nouvelle_date_dt.tzinfo is None:
                nouvelle_date_dt = tz.make_aware(nouvelle_date_dt)

            delta_prolongation = nouvelle_date_dt - resa.date_depart
            if delta_prolongation.total_seconds() < 24 * 3600:
                messages.error(request, "La prolongation doit être d'au moins 24 heures.")
            elif not resa.chambre.is_available_for_dates(resa.date_depart, nouvelle_date_dt, exclude_resa_id=resa.pk):
                messages.error(request, "La chambre n'est pas disponible pour les nouvelles dates.")
            else:
                # ── Calcul correct : différence entre nouveau et ancien montant_chambre ──
                # On capture l'ancien montant AVANT de changer la date
                ancien_montant_chambre = resa.montant_chambre
                ancien_nombre_nuits = resa.nombre_nuits
                old_depart = resa.date_depart

                # Mettre à jour la date de départ
                resa.date_depart = nouvelle_date_dt
                resa.save()

                # Maintenant le model recalcule automatiquement avec la nouvelle date
                nouveau_montant_chambre = resa.montant_chambre
                nouveau_nombre_nuits = resa.nombre_nuits
                nuits_ajoutees = nouveau_nombre_nuits - ancien_nombre_nuits

                # Le montant supplémentaire = exactement la différence de valeur totale des nuits
                montant_supplementaire = nouveau_montant_chambre - ancien_montant_chambre

                Paiement.objects.create(
                    montant_paye=montant_supplementaire,
                    mode=mode_paiement,
                    status='confirme',
                    reservation=resa,
                    client=resa.client,
                    user=user,
                    est_remboursement=False,
                    notes=(
                        f"Prolongation : {ancien_nombre_nuits} nuit(s) → {nouveau_nombre_nuits} nuit(s) "
                        f"(+{nuits_ajoutees} nuit(s)) | "
                        f"{ancien_montant_chambre} → {nouveau_montant_chambre} MRU "
                        f"(+{montant_supplementaire} MRU) | "
                        f"{timezone.localtime(old_depart).strftime('%d/%m/%Y %H:%M')} "
                        f"→ {timezone.localtime(nouvelle_date_dt).strftime('%d/%m/%Y %H:%M')}"
                    ),
                )

                log_action(resa, 'modification',
                    f"Réservation prolongée par {user.email}: "
                    f"{ancien_nombre_nuits}→{nouveau_nombre_nuits} nuit(s) | "
                    f"montant chambre {ancien_montant_chambre}→{nouveau_montant_chambre} MRU | "
                    f"+{montant_supplementaire} MRU payé ({mode_paiement}).",
                    user=user)
                messages.success(request,
                    f"Réservation prolongée jusqu'au {timezone.localtime(nouvelle_date_dt).strftime('%d/%m/%Y à %H:%M')}. "
                    f"Paiement de {montant_supplementaire} MRU enregistré "
                    f"({ancien_nombre_nuits} → {nouveau_nombre_nuits} nuit(s))."
                )
                return redirect('reservation:detail', pk=pk)
        except ValueError:
            messages.error(request, "Date invalide.")

    return render(request, 'admin/reservation/confirm_action.html', {
        'resa': resa,
        'action': 'Prolonger',
        'action_url': request.path,
        'show_date_form': True,
        'today': now.date(),
        'date_min_prolongation': date_min_prolongation.strftime('%Y-%m-%dT%H:%M'),
        'prix_nuit': prix_nuit,
        'date_arrivee_ts': int(resa.date_arrivee.timestamp()) * 1000,
        'date_depart_ts': int(resa.date_depart.timestamp()) * 1000,
        'ancien_nombre_nuits': resa.nombre_nuits,
        'ancien_montant_chambre': resa.montant_chambre,
    })
