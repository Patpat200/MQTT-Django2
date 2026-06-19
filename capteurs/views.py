import json
import csv
from django.shortcuts  import render, get_object_or_404, redirect
from django.db.models  import Avg, Q
from django.http       import HttpResponse
from .models           import Capteur, Mesure
from .forms            import CapteurEditForm, FiltreForm


def liste_capteurs(request):
    capteurs = Capteur.objects.all()
    return render(request, 'capteurs/liste_capteurs.html', {'capteurs': capteurs})


def detail_capteur(request, id_capteur):
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)
    if request.method == 'POST':
        form = CapteurEditForm(request.POST, instance=capteur)
        if form.is_valid():
            form.save()
            return redirect('detail_capteur', id_capteur=id_capteur)
    else:
        form = CapteurEditForm(instance=capteur)
    mesures = Mesure.objects.filter(id_capteur=capteur).order_by('-timestamp_mesure')[:50]
    return render(request, 'capteurs/detail_capteur.html', {
        'capteur': capteur,
        'form':    form,
        'mesures': mesures
    })


def supprimer_capteur(request, id_capteur):
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)
    if request.method == 'POST':
        capteur.delete()
        return redirect('liste_capteurs')
    return render(request, 'capteurs/confirmer_suppression.html', {'capteur': capteur})


def donnees(request):
    form    = FiltreForm(request.GET or None)
    mesures = Mesure.objects.select_related('id_capteur').all()
    if form.is_valid():
        nom_ou_id  = form.cleaned_data.get('nom_ou_id')
        date_debut = form.cleaned_data.get('date_debut')
        date_fin   = form.cleaned_data.get('date_fin')
        if nom_ou_id:
            mesures = mesures.filter(
                Q(id_capteur__nom_capteur__icontains=nom_ou_id) |
                Q(id_capteur__id_capteur__icontains=nom_ou_id)
            )
        if date_debut:
            mesures = mesures.filter(timestamp_mesure__date__gte=date_debut)
        if date_fin:
            mesures = mesures.filter(timestamp_mesure__date__lte=date_fin)
    temp_moyenne = mesures.aggregate(Avg('temperature'))['temperature__avg']
    return render(request, 'capteurs/donnees.html', {
        'form':         form,
        'mesures':      mesures.order_by('-timestamp_mesure')[:200],
        'temp_moyenne': round(float(temp_moyenne), 2) if temp_moyenne else None
    })


def graphique(request, id_capteur):
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)
    mesures = Mesure.objects.filter(id_capteur=capteur).order_by('timestamp_mesure')[:100]
    labels  = [str(m.timestamp_mesure) for m in mesures]
    valeurs = [float(m.temperature)    for m in mesures]
    return render(request, 'capteurs/graphique.html', {
        'capteur': capteur,
        'labels':  json.dumps(labels),
        'valeurs': json.dumps(valeurs)
    })


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donnees_sae204.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID Mesure', 'ID Capteur', 'Nom', 'Pièce', 'Timestamp', 'Temp (°C)'])
    for m in Mesure.objects.select_related('id_capteur').order_by('-timestamp_mesure'):
        writer.writerow([
            m.id_mesure,
            m.id_capteur.id_capteur,
            m.id_capteur.nom_capteur,
            m.id_capteur.piece,
            m.timestamp_mesure,
            m.temperature
        ])
    return response