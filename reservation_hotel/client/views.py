from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.cache import never_cache
from client.models import Client
from chambre.models import TypeChambre, Chambre
from hotel.models import Hotel
from ville.models import Ville
from reservation.models import Reservation, ReservationService, EvaluationService
from paiement.models import Paiement, PaiementBankily, PaiementVisa
from users.decorators import client_required
import datetime


def home(request):
    from django.db.models import Avg, Count
    villes = Ville.objects.filter(hotels__isnull=False).distinct()
    from services.models import Service
    # Stats d'évaluations par service (uniquement services avec au moins 1 évaluation)
    services_evalues = Service.objects.filter(
        actif=True,
        evaluationservice__isnull=False
    ).annotate(
        moyenne=Avg('evaluationservice__note'),
        nb_evaluations=Count('evaluationservice')
    ).order_by('-moyenne')[:8]

    return render(request, 'client/home.html', {
        'villes': villes,
        'services_evalues': services_evalues,
    })


def recherche_chambres(request):
    from collections import defaultdict
    ville_id = request.GET.get('ville')
    date_arrivee = request.GET.get('date_arrivee')
    date_depart = request.GET.get('date_depart')
    adultes = int(request.GET.get('adultes', 1))
    enfants = int(request.GET.get('enfants', 0))
    total_personnes = adultes + enfants
    recherche_active = bool(ville_id and date_arrivee and date_depart)

    chambres_disponibles = []
    chambres_vitrine = []   # 3 par hôtel sans filtre dates
    ville = None
    erreur = None
    nombre_nuits = 0

    villes = Ville.objects.filter(hotels__isnull=False).distinct()

    if recherche_active:
        # ── Recherche avec ville + dates ──────────────────────────────
        try:
            date_arrivee_dt = datetime.date.fromisoformat(date_arrivee)
            date_depart_dt = datetime.date.fromisoformat(date_depart)
            today = timezone.now().date()

            tomorrow = today + datetime.timedelta(days=1)
            if date_arrivee_dt < tomorrow:
                erreur = "La réservation doit être effectuée au moins 24h à l'avance. La date d'arrivée minimum est demain."
            elif date_depart_dt < date_arrivee_dt:
                erreur = "La date de départ doit être après la date d'arrivée."
            elif total_personnes < 1:
                erreur = "Au moins une personne requise."
            else:
                ville = get_object_or_404(Ville, pk=ville_id)
                nombre_nuits = max((date_depart_dt - date_arrivee_dt).days, 1)

                if total_personnes >= 5:
                    capacite_filter = {'type_chambre__capacite': 5}
                else:
                    capacite_filter = {'type_chambre__capacite__gte': total_personnes}

                date_fin_eff = date_depart_dt if date_depart_dt > date_arrivee_dt else date_arrivee_dt + datetime.timedelta(days=1)

                chambres_qs = Chambre.objects.filter(
                    hotel__ville=ville,
                    etat='disponible',
                    **capacite_filter
                ).select_related('hotel', 'type_chambre').prefetch_related(
                    'type_chambre__equipements'
                ).exclude(
                    reservations__statut__in=['en_attente', 'confirmee', 'checkin'],
                    reservations__date_arrivee__lt=date_fin_eff,
                    reservations__date_depart__gt=date_arrivee_dt,
                ).order_by('hotel__nom', 'type_chambre__prix_nuit', 'numero')

                # Max 3 par hôtel
                par_hotel = defaultdict(list)
                for c in chambres_qs:
                    if len(par_hotel[c.hotel_id]) < 3:
                        par_hotel[c.hotel_id].append(c)
                chambres_disponibles = [c for lst in par_hotel.values() for c in lst]

        except ValueError:
            erreur = "Dates invalides."
    else:
        # ── Page d'accueil recherche : vitrine 3 chambres par hôtel ──
        qs = Chambre.objects.filter(
            etat='disponible'
        ).select_related('hotel', 'type_chambre').prefetch_related(
            'type_chambre__equipements'
        ).order_by('hotel__nom', 'type_chambre__prix_nuit', 'numero')

        par_hotel = defaultdict(list)
        for c in qs:
            if len(par_hotel[c.hotel_id]) < 3:
                par_hotel[c.hotel_id].append(c)
        chambres_vitrine = [c for lst in par_hotel.values() for c in lst]

    return render(request, 'client/recherche.html', {
        'villes': villes,
        'chambres_disponibles': chambres_disponibles,
        'chambres_vitrine': chambres_vitrine,
        'recherche_active': recherche_active,
        'ville': ville,
        'ville_id': ville_id,
        'date_arrivee': date_arrivee,
        'date_depart': date_depart,
        'adultes': adultes,
        'enfants': enfants,
        'erreur': erreur,
        'nombre_nuits': nombre_nuits,
    })


def client_login(request):
    if request.session.get('client_id'):
        return redirect('client:mes_reservations')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()

        try:
            client = Client.objects.get(email=email, telephone=telephone)
            request.session['client_id'] = client.pk
            messages.success(request, f"Bienvenue, {client.prenom}!")
            return redirect('client:mes_reservations')
        except Client.DoesNotExist:
            messages.error(request, "Email ou téléphone incorrect.")

    return render(request, 'client/login.html')


def client_logout(request):
    if 'client_id' in request.session:
        del request.session['client_id']
    return redirect('client:home')


@never_cache
def reserver(request):
    ville_id = request.GET.get('ville') or request.POST.get('ville')
    chambre_id = request.GET.get('chambre') or request.POST.get('chambre')
    date_arrivee = request.GET.get('date_arrivee') or request.POST.get('date_arrivee')
    date_depart = request.GET.get('date_depart') or request.POST.get('date_depart')
    adultes = int(request.GET.get('adultes', 1) or request.POST.get('adultes', 1))
    enfants = int(request.GET.get('enfants', 0) or request.POST.get('enfants', 0))

    if not all([chambre_id, date_arrivee, date_depart]):
        return redirect('client:recherche')

    chambre = get_object_or_404(Chambre, pk=chambre_id)
    type_chambre = chambre.type_chambre
    ville = chambre.hotel.ville
    hotel = chambre.hotel

    try:
        date_arrivee_dt = datetime.date.fromisoformat(date_arrivee)
        date_depart_dt = datetime.date.fromisoformat(date_depart)
    except ValueError:
        return redirect('client:recherche')

    nombre_nuits = max((date_depart_dt - date_arrivee_dt).days, 1)
    montant_chambre = type_chambre.prix_nuit * nombre_nuits

    # Validations
    today = timezone.now().date()
    tomorrow = today + datetime.timedelta(days=1)
    total_personnes = adultes + enfants

    if date_arrivee_dt < tomorrow:
        messages.error(request, "La réservation doit être effectuée au moins 24h à l'avance.")
        return redirect('client:recherche')

    if total_personnes > type_chambre.capacite:
        messages.error(request, f"Le nombre de personnes ({total_personnes}) dépasse la capacité ({type_chambre.capacite}).")
        return redirect('client:recherche')

    if request.method == 'POST' and request.POST.get('etape') == 'final':
        # ── Récupérer toutes les infos ──────────────────────────────
        email = request.POST.get('email', '').strip()
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        nationalite = request.POST.get('nationalite', '').strip()
        type_identite = request.POST.get('type_identite', 'CNI')
        mode = request.POST.get('mode_paiement', '')

        errors = []
        if not all([email, nom, prenom, telephone]):
            errors.append("Tous les champs personnels sont requis.")
        if not mode:
            errors.append("Veuillez choisir un mode de paiement.")
        if mode == 'bankily' and not hotel.num_bankily:
            errors.append("Le paiement Bankily n'est pas disponible pour cet hôtel.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            # Client (créer ou récupérer)
            client, created = Client.objects.get_or_create(
                email=email,
                defaults={
                    'nom': nom, 'prenom': prenom, 'telephone': telephone,
                    'nationalite': nationalite, 'type_identite': type_identite,
                    'hash_mdp': ''
                }
            )

            # ── Mode Bankily : stocker en session, NE PAS créer la réservation ──
            if not chambre.is_available_for_dates(date_arrivee_dt, date_depart_dt):
                messages.error(request, "Désolé, cette chambre vient d'être réservée. Veuillez en choisir une autre.")
                return redirect('client:recherche')

            # ── Mode Bankily : stocker en session, NE PAS créer la réservation ──
            if mode == 'bankily':
                # On stocke toutes les données dans la session
                # La réservation sera créée SEULEMENT après soumission des infos Bankily
                request.session['pending_resa'] = {
                    'email': email,
                    'nom': nom,
                    'prenom': prenom,
                    'telephone': telephone,
                    'nationalite': nationalite,
                    'type_identite': type_identite,
                    'chambre_id': int(chambre_id),
                    'date_arrivee': date_arrivee,
                    'date_depart': date_depart,
                    'adultes': adultes,
                    'enfants': enfants,
                    'montant_total': float(montant_chambre),
                }
                return render(request, 'client/bankily_info.html', {
                    'hotel': hotel,
                    'montant_total': montant_chambre,
                    'pending_mode': True,
                })

    context = {
        'chambre': chambre,
        'type_chambre': type_chambre,
        'hotel': hotel,
        'ville': ville,
        'date_arrivee': date_arrivee,
        'date_depart': date_depart,
        'adultes': adultes,
        'enfants': enfants,
        'nombre_nuits': nombre_nuits,
        'montant_chambre': montant_chambre,
    }
    return render(request, 'client/reserver.html', context)


@never_cache
def paiement_reservation(request):
    token = request.session.get('resa_token')
    client_id = request.session.get('client_id')

    if not token or not client_id:
        messages.error(request, "Session expirée. Veuillez recommencer.")
        return redirect('client:recherche')

    try:
        parts = token.split('-')
        resa_id = int(parts[1])
        resa = Reservation.objects.get(pk=resa_id, client_id=client_id, statut='en_attente')
    except (ValueError, IndexError, Reservation.DoesNotExist):
        messages.error(request, "Réservation introuvable.")
        return redirect('client:recherche')

    hotel = resa.chambre.hotel

    if request.method == 'POST':
        mode = request.POST.get('mode')

        if mode == 'bankily':
            # Afficher numéro bankily de l'hôtel
            if not hotel.num_bankily:
                messages.error(request, "Le paiement Bankily n'est pas disponible pour cet hôtel.")
            else:
                # Créer un paiement en attente SANS code transaction (le client va le fournir)
                paiement = Paiement.objects.create(
                    montant_paye=resa.montant_total,
                    mode='bankily',
                    status='en_attente',
                    reservation=resa,
                    client=resa.client,
                )
                # Créer l'enregistrement Bankily vide (le client remplira code + capture)
                PaiementBankily.objects.create(
                    paiement=paiement,
                    numero_bankily=hotel.num_bankily,
                    code_transaction='',
                )
                request.session['paiement_id'] = paiement.pk
                return render(request, 'client/bankily_info.html', {
                    'resa': resa,
                    'hotel': hotel,
                    'paiement': paiement,
                })

        elif mode == 'visa':
            numero_carte = request.POST.get('numero_carte', '').replace(' ', '')
            titulaire = request.POST.get('titulaire', '').strip()
            expiration = request.POST.get('expiration', '').strip()
            cvv = request.POST.get('cvv', '').strip()

            # Validation basique Visa
            if len(numero_carte) not in [13, 16, 19]:
                messages.error(request, "Numéro de carte invalide.")
            elif not titulaire:
                messages.error(request, "Nom du titulaire requis.")
            elif not expiration or len(expiration) != 5:
                messages.error(request, "Date d'expiration invalide (MM/AA).")
            elif len(cvv) not in [3, 4]:
                messages.error(request, "CVV invalide.")
            else:
                from django.contrib.auth.hashers import make_password
                paiement = Paiement.objects.create(
                    montant_paye=resa.montant_total,
                    mode='visa',
                    status='confirme',
                    reservation=resa,
                    client=resa.client,
                )
                PaiementVisa.objects.create(
                    paiement=paiement,
                    numero_carte=numero_carte,
                    titulaire=titulaire,
                    expiration=expiration,
                    cvv_hash=make_password(cvv),
                    transaction_id=f"VIS{paiement.pk:08d}",
                )
                # Confirmer la réservation
                resa.statut = 'confirmee'
                resa.save()

                from reservation.models import HistoriqueReservation
                HistoriqueReservation.objects.create(
                    reservation=resa,
                    action='paiement',
                    description=f"Paiement Visa de {paiement.montant_paye} MRU confirmé automatiquement.",
                    email_client=resa.client.email,
                )
                HistoriqueReservation.objects.create(
                    reservation=resa,
                    action='confirmation',
                    description=f"Réservation confirmée après paiement Visa. Chambre: {resa.chambre.numero}",
                    email_client=resa.client.email,
                )

                del request.session['resa_token']
                messages.success(request, f"Réservation confirmée! Votre chambre est la {resa.chambre.numero}.")
                return redirect('client:confirmation_reservation')

    return render(request, 'client/paiement.html', {
        'resa': resa,
        'hotel': hotel,
    })


@never_cache
def confirmation_reservation(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return redirect('client:home')

    # Dernière réservation confirmée du client
    resa = Reservation.objects.filter(
        client_id=client_id,
        statut__in=['confirmee', 'checkin']
    ).order_by('-date_creation').first()

    return render(request, 'client/confirmation.html', {'resa': resa})


@client_required
@never_cache
def mes_reservations(request):
    client = request.current_client

    # Auto-delete reservations en_attente older than 2 hours (no payment made)
    expiry_threshold = timezone.now() - datetime.timedelta(hours=2)
    old_unpaid = Reservation.objects.filter(
        client=client,
        statut='en_attente',
        date_creation__lt=expiry_threshold,
        paiements__isnull=True
    )
    old_unpaid.delete()

    reservations = Reservation.objects.filter(
        client=client
    ).select_related('chambre', 'chambre__type_chambre', 'chambre__hotel').order_by('-date_creation')

    return render(request, 'client/mes_reservations.html', {
        'reservations': reservations,
        'client': client,
    })


@client_required
@never_cache
def detail_reservation(request, token):
    client = request.current_client
    # Token = hash basé sur id + client_id pour sécurité
    try:
        import hashlib
        reservations = Reservation.objects.filter(client=client)
        resa = None
        for r in reservations:
            expected_token = hashlib.sha256(f"{r.pk}-{client.pk}-SECRET".encode()).hexdigest()[:16]
            if expected_token == token:
                resa = r
                break
        if not resa:
            raise ValueError("Token invalide")
    except (ValueError, Exception):
        messages.error(request, "Réservation introuvable.")
        return redirect('client:mes_reservations')

    services_dispo = []
    if resa.statut == 'checkin':
        from services.models import Service
        services_dispo = Service.objects.filter(actif=True)

    return render(request, 'client/detail_reservation.html', {
        'resa': resa,
        'services_dispo': services_dispo,
    })


@client_required
def annuler_reservation(request, token):
    client = request.current_client
    try:
        import hashlib
        reservations = Reservation.objects.filter(client=client)
        resa = None
        for r in reservations:
            expected_token = hashlib.sha256(f"{r.pk}-{client.pk}-SECRET".encode()).hexdigest()[:16]
            if expected_token == token:
                resa = r
                break
        if not resa:
            raise ValueError("Token invalide")
    except Exception:
        messages.error(request, "Réservation introuvable.")
        return redirect('client:mes_reservations')

    if resa.statut not in ['en_attente', 'confirmee']:
        messages.error(request, "Cette réservation ne peut pas être annulée.")
        return redirect('client:mes_reservations')

    if request.method == 'POST':
        montant_paye = resa.montant_paye
        now = timezone.now()
        delai = now - resa.date_creation
        remboursement_possible = delai.total_seconds() < 86400 and float(montant_paye) > 0

        resa.statut = 'annulee'
        resa.save()

        from reservation.models import HistoriqueReservation
        if remboursement_possible:
            desc = f"Réservation annulée dans les 24h. Remboursement de {montant_paye} MRU prévu."
            msg = f"Réservation annulée. Un remboursement de {montant_paye} MRU sera effectué."
        else:
            desc = "Réservation annulée après 24h. Aucun remboursement (politique annulation)."
            msg = "Réservation annulée. Aucun remboursement possible (annulation après 24h)."

        HistoriqueReservation.objects.create(
            reservation=resa,
            action='annulation',
            description=desc,
            email_client=client.email,
        )
        messages.success(request, msg)
        return redirect('client:mes_reservations')

    now = timezone.now()
    delai = now - resa.date_creation
    remboursement_possible = delai.total_seconds() < 86400 and float(resa.montant_paye) > 0
    return render(request, 'client/annuler_confirmation.html', {'resa': resa, 'remboursement_possible': remboursement_possible})


@client_required
def evaluer_service(request, resa_token, service_id):
    client = request.current_client
    from services.models import Service
    import hashlib

    try:
        reservations = Reservation.objects.filter(client=client)
        resa = None
        for r in reservations:
            expected_token = hashlib.sha256(f"{r.pk}-{client.pk}-SECRET".encode()).hexdigest()[:16]
            if expected_token == resa_token:
                resa = r
                break
        if not resa:
            raise ValueError
    except Exception:
        messages.error(request, "Réservation introuvable.")
        return redirect('client:mes_reservations')

    if resa.statut != 'checkin':
        messages.error(request, "Vous ne pouvez évaluer les services qu'en cours de séjour.")
        return redirect('client:mes_reservations')

    service = get_object_or_404(Service, pk=service_id)

    if request.method == 'POST':
        note = int(request.POST.get('note', 0))
        commentaire = request.POST.get('commentaire', '').strip()
        if 1 <= note <= 5:
            EvaluationService.objects.update_or_create(
                reservation=resa,
                service=service,
                defaults={'note': note, 'commentaire': commentaire}
            )
            messages.success(request, "Évaluation enregistrée!")
        else:
            messages.error(request, "Note invalide (1-5).")

    return redirect('client:detail_reservation', token=resa_token)


@never_cache
def soumettre_bankily(request):
    """Le client soumet ses infos Bankily.
    La réservation est créée ICI pour la première fois si pending_resa est en session.
    """
    if request.method != 'POST':
        return redirect('client:recherche')

    code_transaction = request.POST.get('code_transaction', '').strip()
    numero_client = request.POST.get('numero_client_bankily', '').strip()
    capture = request.FILES.get('capture_ecran')

    # ── Cas 1 : nouvelle réservation depuis session (pending_resa) ─────────
    pending = request.session.get('pending_resa')
    if pending:
        chambre_id = pending.get('chambre_id')
        chambre = get_object_or_404(Chambre, pk=chambre_id)
        hotel = chambre.hotel
        montant_total = pending.get('montant_total', 0)

        # Validation des champs Bankily
        errors = []
        if not code_transaction:
            errors.append("Le code de transaction Bankily est obligatoire.")
        if not numero_client:
            errors.append("Votre numéro Bankily est obligatoire.")
        if not capture:
            errors.append("La capture d'écran du virement est obligatoire.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'client/bankily_info.html', {
                'hotel': hotel,
                'montant_total': montant_total,
                'pending_mode': True,
            })

        # Vérifier disponibilité de la chambre une dernière fois
        date_arrivee_dt = datetime.date.fromisoformat(pending['date_arrivee'])
        date_depart_dt = datetime.date.fromisoformat(pending['date_depart'])
        if not chambre.is_available_for_dates(date_arrivee_dt, date_depart_dt):
            messages.error(request, "Désolé, cette chambre vient d'être réservée. Veuillez en choisir une autre.")
            request.session.pop('pending_resa', None)
            return redirect('client:recherche')

        # Tout est valide : créer client + réservation + paiement en une seule fois
        client, _ = Client.objects.get_or_create(
            email=pending['email'],
            defaults={
                'nom': pending['nom'], 'prenom': pending['prenom'],
                'telephone': pending['telephone'], 'nationalite': pending['nationalite'],
                'type_identite': pending['type_identite'], 'hash_mdp': ''
            }
        )

        resa = Reservation.objects.create(
            date_arrivee=date_arrivee_dt,
            date_depart=date_depart_dt,
            nbr_adultes=pending['adultes'],
            nbr_enfants=pending['enfants'],
            statut='en_attente',
            client=client,
            chambre=chambre,
        )

        paiement = Paiement.objects.create(
            montant_paye=resa.montant_total,
            mode='bankily',
            status='en_attente',
            reservation=resa,
            client=client,
        )

        PaiementBankily.objects.create(
            paiement=paiement,
            numero_bankily=hotel.num_bankily,
            code_transaction=code_transaction,
            numero_client=numero_client,
            capture_ecran=capture,
        )

        from reservation.models import HistoriqueReservation
        HistoriqueReservation.objects.create(
            reservation=resa,
            action='creation',
            description=(
                f"Réservation créée par {client.prenom} {client.nom}. "
                f"Preuve Bankily soumise. Code: {code_transaction}"
            ),
            email_client=client.email,
        )

        request.session['client_id'] = client.pk
        request.session.pop('pending_resa', None)

        messages.success(
            request,
            "Votre réservation a bien été enregistrée. "
            "Notre équipe va vérifier votre paiement Bankily et confirmer votre réservation."
        )
        return redirect('client:mes_reservations')

    # ── Cas 2 : mise à jour d'un paiement Bankily existant ────────────────
    paiement_id = request.POST.get('paiement_id') or request.session.get('paiement_id')
    client_id = request.session.get('client_id')

    if not paiement_id or not client_id:
        messages.error(request, "Session expirée. Veuillez recommencer.")
        return redirect('client:recherche')

    try:
        paiement = Paiement.objects.get(
            pk=paiement_id,
            client_id=client_id,
            mode='bankily',
            status='en_attente',
        )
    except Paiement.DoesNotExist:
        messages.error(request, "Paiement introuvable ou déjà traité.")
        return redirect('client:mes_reservations')

    resa = paiement.reservation
    hotel = resa.chambre.hotel

    errors = []
    if not code_transaction:
        errors.append("Le code de transaction Bankily est obligatoire.")
    if not numero_client:
        errors.append("Votre numéro Bankily est obligatoire.")
    if not capture:
        errors.append("La capture d'écran du virement est obligatoire.")

    if errors:
        for e in errors:
            messages.error(request, e)
        return render(request, 'client/bankily_info.html', {
            'resa': resa, 'hotel': hotel, 'paiement': paiement,
        })

    try:
        bankily = paiement.bankily_detail
    except PaiementBankily.DoesNotExist:
        bankily = PaiementBankily(paiement=paiement, numero_bankily=hotel.num_bankily)

    bankily.code_transaction = code_transaction
    bankily.numero_client = numero_client
    bankily.capture_ecran = capture
    bankily.save()

    from reservation.models import HistoriqueReservation
    HistoriqueReservation.objects.create(
        reservation=resa,
        action='paiement',
        description=f"Client a soumis preuve de paiement Bankily. Code: {code_transaction}",
        email_client=paiement.client.email,
    )

    request.session.pop('resa_token', None)
    request.session.pop('paiement_id', None)

    messages.success(request, "Votre preuve de paiement a été envoyée. Notre équipe va vérifier et confirmer votre réservation.")
    return redirect('client:mes_reservations')
