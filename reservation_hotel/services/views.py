from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from services.models import Service
from users.decorators import staff_required, role_required


@staff_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'admin/services/list.html', {'services': services})


@staff_required
@role_required('admin', 'manager')
def service_create(request):
    if request.method == 'POST':
        nom = request.POST.get('nom_service', '').strip()
        description = request.POST.get('description', '')
        prix = request.POST.get('prix', 0)
        categorie = request.POST.get('categorie', 'autre')
        if not nom:
            messages.error(request, "Nom du service requis.")
        else:
            Service.objects.create(nom_service=nom, description=description, prix=prix, categorie=categorie)
            messages.success(request, f"Service '{nom}' créé.")
            return redirect('services:list')

    return render(request, 'admin/services/form.html', {
        'action': 'Créer',
        'categorie_choices': Service.CATEGORIE_CHOICES,
    })


@staff_required
@role_required('admin', 'manager')
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.nom_service = request.POST.get('nom_service', service.nom_service).strip()
        service.description = request.POST.get('description', service.description)
        service.prix = request.POST.get('prix', service.prix)
        service.categorie = request.POST.get('categorie', service.categorie)
        service.actif = bool(request.POST.get('actif'))
        service.save()
        messages.success(request, "Service modifié.")
        return redirect('services:list')

    return render(request, 'admin/services/form.html', {
        'service': service, 'action': 'Modifier',
        'categorie_choices': Service.CATEGORIE_CHOICES,
    })


@staff_required
@role_required('admin', 'manager')
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service supprimé.")
        return redirect('services:list')
    return render(request, 'admin/services/delete_confirm.html', {'service': service})
