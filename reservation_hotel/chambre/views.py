from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from chambre.models import Chambre, TypeChambre, Equipement
from hotel.models import Hotel
from users.decorators import staff_required, role_required


@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def chambre_list(request):
    user = request.current_user
    if user.role == 'admin':
        chambres = Chambre.objects.select_related('type_chambre', 'hotel').all()
        hotels = Hotel.objects.all()
    else:
        chambres = Chambre.objects.filter(hotel=user.hotel).select_related('type_chambre', 'hotel')
        hotels = Hotel.objects.filter(pk=user.hotel_id)

    hotel_filter = request.GET.get('hotel', '')
    etat_filter = request.GET.get('etat', '')
    type_filter = request.GET.get('type', '')
    search = request.GET.get('q', '')

    if hotel_filter and user.role == 'admin':
        chambres = chambres.filter(hotel_id=hotel_filter)
    if etat_filter:
        chambres = chambres.filter(etat=etat_filter)
    if type_filter:
        chambres = chambres.filter(type_chambre_id=type_filter)
    if search:
        chambres = chambres.filter(Q(numero__icontains=search))

    return render(request, 'admin/chambre/list.html', {
        'chambres': chambres,
        'hotels': hotels,
        'types': TypeChambre.objects.all(),
        'etat_choices': Chambre.ETAT_CHOICES,
        'hotel_filter': hotel_filter,
        'etat_filter': etat_filter,
        'type_filter': type_filter,
        'search': search,
    })


@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def chambre_create(request):
    user = request.current_user
    hotels = Hotel.objects.all() if user.role == 'admin' else Hotel.objects.filter(pk=user.hotel_id)
    types = TypeChambre.objects.all()

    if request.method == 'POST':
        numero = request.POST.get('numero', '').strip()
        etage = int(request.POST.get('etage', 0))
        etat = request.POST.get('etat', 'disponible')
        type_id = request.POST.get('type_chambre')
        hotel_id = request.POST.get('hotel') if user.role == 'admin' else user.hotel_id
        image = request.FILES.get('image')

        if Chambre.objects.filter(numero=numero, hotel_id=hotel_id).exists():
            messages.error(request, f"Une chambre numéro {numero} existe déjà dans cet hôtel.")
        elif not type_id:
            messages.error(request, "Type de chambre requis.")
        else:
            chambre = Chambre(
                numero=numero, etage=etage, etat=etat,
                type_chambre_id=type_id, hotel_id=hotel_id
            )
            if image:
                chambre.image = image
            chambre.save()
            messages.success(request, f"Chambre {numero} créée avec succès.")
            return redirect('chambre:list')

    return render(request, 'admin/chambre/form.html', {
        'hotels': hotels, 'types': types, 'action': 'Créer',
        'etat_choices': Chambre.ETAT_CHOICES,
    })


@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def chambre_edit(request, pk):
    user = request.current_user
    chambre = get_object_or_404(Chambre, pk=pk)

    if user.role != 'admin' and chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('chambre:list')

    hotels = Hotel.objects.all() if user.role == 'admin' else Hotel.objects.filter(pk=user.hotel_id)
    types = TypeChambre.objects.all()

    if request.method == 'POST':
        chambre.numero = request.POST.get('numero', chambre.numero).strip()
        chambre.etage = int(request.POST.get('etage', chambre.etage))
        chambre.etat = request.POST.get('etat', chambre.etat)
        chambre.type_chambre_id = request.POST.get('type_chambre', chambre.type_chambre_id)
        if user.role == 'admin':
            chambre.hotel_id = request.POST.get('hotel', chambre.hotel_id)
        image = request.FILES.get('image')
        if image:
            chambre.image = image
        chambre.save()
        messages.success(request, "Chambre modifiée avec succès.")
        return redirect('chambre:list')

    return render(request, 'admin/chambre/form.html', {
        'chambre': chambre, 'hotels': hotels, 'types': types,
        'action': 'Modifier', 'etat_choices': Chambre.ETAT_CHOICES,
    })


@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def chambre_delete(request, pk):
    user = request.current_user
    chambre = get_object_or_404(Chambre, pk=pk)

    if user.role != 'admin' and chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('chambre:list')

    # Vérifier si réservation active
    if chambre.reservations.filter(statut__in=['en_attente', 'confirmee', 'checkin']).exists():
        messages.error(request, "Impossible de supprimer: chambre avec réservations actives.")
        return redirect('chambre:list')

    if request.method == 'POST':
        chambre.delete()
        messages.success(request, "Chambre supprimée.")
        return redirect('chambre:list')

    return render(request, 'admin/chambre/delete_confirm.html', {'chambre': chambre})


# Type de Chambre CRUD
@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def type_list(request):
    types = TypeChambre.objects.prefetch_related('equipements').all()
    return render(request, 'admin/chambre/type_list.html', {'types': types})


@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def type_create(request):
    equipements = Equipement.objects.all()

    if request.method == 'POST':
        libelle = request.POST.get('libelle', '').strip()
        prix = request.POST.get('prix_nuit', 0)
        capacite = int(request.POST.get('capacite', 1))
        description = request.POST.get('description', '')
        equip_ids = request.POST.getlist('equipements')

        if not libelle:
            messages.error(request, "Libellé requis.")
        else:
            tc = TypeChambre(libelle=libelle, prix_nuit=prix, capacite=capacite, description=description)
            tc.save()
            if equip_ids:
                tc.equipements.set(equip_ids)
            messages.success(request, f"Type '{libelle}' créé.")
            return redirect('chambre:type_list')

    return render(request, 'admin/chambre/type_form.html', {
        'equipements': equipements, 'action': 'Créer'
    })


@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def type_edit(request, pk):
    tc = get_object_or_404(TypeChambre, pk=pk)
    equipements = Equipement.objects.all()

    if request.method == 'POST':
        tc.libelle = request.POST.get('libelle', tc.libelle).strip()
        tc.prix_nuit = request.POST.get('prix_nuit', tc.prix_nuit)
        tc.capacite = int(request.POST.get('capacite', tc.capacite))
        tc.description = request.POST.get('description', tc.description)
        equip_ids = request.POST.getlist('equipements')
        tc.save()
        tc.equipements.set(equip_ids)
        messages.success(request, "Type de chambre modifié.")
        return redirect('chambre:type_list')

    return render(request, 'admin/chambre/type_form.html', {
        'tc': tc, 'equipements': equipements, 'action': 'Modifier'
    })


@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def type_delete(request, pk):
    tc = get_object_or_404(TypeChambre, pk=pk)
    if tc.chambres.exists():
        messages.error(request, "Impossible: des chambres utilisent ce type.")
        return redirect('chambre:type_list')
    if request.method == 'POST':
        tc.delete()
        messages.success(request, "Type supprimé.")
        return redirect('chambre:type_list')
    return render(request, 'admin/chambre/type_delete_confirm.html', {'tc': tc})


# Équipements
@staff_required
@role_required('admin', 'manager', 'gestion_chambre')
def equipement_list(request):
    equips = Equipement.objects.all()
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        if nom:
            Equipement.objects.get_or_create(nom=nom)
            messages.success(request, f"Équipement '{nom}' ajouté.")
        return redirect('chambre:equipement_list')
    return render(request, 'admin/chambre/equipement_list.html', {'equips': equips})
