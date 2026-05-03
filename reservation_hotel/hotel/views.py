from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from hotel.models import Hotel
from ville.models import Ville
from users.decorators import staff_required, role_required


@staff_required
@role_required('admin')
def hotel_list(request):
    hotels = Hotel.objects.select_related('ville').all()
    return render(request, 'admin/hotel/list.html', {'hotels': hotels})


@staff_required
@role_required('admin')
def hotel_create(request):
    villes = Ville.objects.all()
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        num_bankily = request.POST.get('num_bankily', '').strip()
        ville_id = request.POST.get('ville')
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        if not nom or not adresse or not ville_id:
            messages.error(request, "Nom, adresse et ville requis.")
        else:
            hotel = Hotel(nom=nom, adresse=adresse, num_bankily=num_bankily,
                         ville_id=ville_id, email=email, telephone=telephone, description=description)
            if image:
                hotel.image = image
            hotel.save()
            messages.success(request, f"Hôtel '{nom}' créé.")
            return redirect('hotel:list')
    return render(request, 'admin/hotel/form.html', {'villes': villes, 'action': 'Créer'})


@staff_required
@role_required('admin', 'manager')
def hotel_edit(request, pk):
    user = request.current_user
    hotel = get_object_or_404(Hotel, pk=pk)
    if user.role != 'admin' and user.hotel != hotel:
        messages.error(request, "Accès refusé.")
        return redirect('users:dashboard')
    villes = Ville.objects.all()
    if request.method == 'POST':
        hotel.nom = request.POST.get('nom', hotel.nom).strip()
        hotel.adresse = request.POST.get('adresse', hotel.adresse).strip()
        hotel.num_bankily = request.POST.get('num_bankily', hotel.num_bankily).strip()
        hotel.email = request.POST.get('email', hotel.email).strip()
        hotel.telephone = request.POST.get('telephone', hotel.telephone).strip()
        hotel.description = request.POST.get('description', hotel.description)
        if user.role == 'admin':
            hotel.ville_id = request.POST.get('ville', hotel.ville_id)
        image = request.FILES.get('image')
        if image:
            hotel.image = image
        hotel.save()
        messages.success(request, "Hôtel modifié.")
        return redirect('hotel:list')
    return render(request, 'admin/hotel/form.html', {'hotel': hotel, 'villes': villes, 'action': 'Modifier'})
