from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ville.models import Ville
from users.decorators import staff_required, role_required


@staff_required
@role_required('admin')
def ville_list(request):
    villes = Ville.objects.all()
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        if nom:
            Ville.objects.get_or_create(nom=nom)
            messages.success(request, f"Ville '{nom}' ajoutée.")
        return redirect('ville:list')
    return render(request, 'admin/hotel/ville_list.html', {'villes': villes})


@staff_required
@role_required('admin')
def ville_delete(request, pk):
    ville = get_object_or_404(Ville, pk=pk)
    if ville.hotels.exists():
        messages.error(request, "Impossible: des hôtels sont dans cette ville.")
    else:
        ville.delete()
        messages.success(request, "Ville supprimée.")
    return redirect('ville:list')
