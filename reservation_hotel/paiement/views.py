from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from paiement.models import Paiement
from reservation.models import Reservation
from users.decorators import staff_required, role_required


@staff_required
def paiement_list(request):
    user = request.current_user
    if user.role == 'admin':
        paiements = Paiement.objects.select_related('reservation', 'client').all()
    else:
        paiements = Paiement.objects.filter(
            reservation__chambre__hotel=user.hotel
        ).select_related('reservation', 'client')

    return render(request, 'admin/paiement/list.html', {
        'paiements': paiements.order_by('-date_paiement')[:200],
    })


@staff_required
@role_required('admin', 'manager', 'receptionniste')
def ajouter_paiement(request, resa_pk):
    user = request.current_user
    resa = get_object_or_404(Reservation, pk=resa_pk)

    if user.role != 'admin' and resa.chambre.hotel != user.hotel:
        messages.error(request, "Accès refusé.")
        return redirect('reservation:list')

    if resa.statut not in ['en_attente', 'confirmee', 'checkin']:
        messages.error(request, "Paiement impossible pour cette réservation.")
        return redirect('reservation:detail', pk=resa_pk)

    if resa.montant_restant <= 0:
        messages.error(request, "Aucun montant restant à payer pour cette réservation.")
        return redirect('reservation:detail', pk=resa_pk)

    if request.method == 'POST':
        montant = float(request.POST.get('montant', 0))
        mode = request.POST.get('mode', 'especes')

        if montant <= 0:
            messages.error(request, "Montant invalide.")
        else:
            paiement = Paiement.objects.create(
                montant_paye=montant,
                mode=mode,
                status='confirme',
                reservation=resa,
                client=resa.client,
                user=user,
                notes=request.POST.get('notes', ''),
            )

            if resa.statut == 'en_attente':
                resa.statut = 'confirmee'
                resa.user_confirme = user
                resa.save()

            from reservation.views import log_action
            log_action(resa, 'paiement',
                       f"Paiement {montant} MRU ({mode}) enregistré par {user.email}",
                       user=user)
            messages.success(request, f"Paiement de {montant} MRU enregistré.")
            return redirect('reservation:detail', pk=resa_pk)

    return render(request, 'admin/paiement/form.html', {
        'resa': resa,
        'montant_restant': resa.montant_restant,
        'modes': Paiement.MODE_CHOICES,
    })
