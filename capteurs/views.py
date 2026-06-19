import json
import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from .models import Capteur, Mesure
from .forms import CapteurEditForm, FiltreForm


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

    contexte = {
        'capteur': capteur,
        'form': form,
        'mesures': mesures,
    }
    return render(request, 'capteurs/detail_capteur.html', contexte)


def supprimer_capteur(request, id_capteur):
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)

    if request.method == 'POST':
        capteur.delete()
        return redirect('liste_capteurs')

    return render(request, 'capteurs/confirmer_suppression.html', {'capteur': capteur})


def donnees(request):
    form = FiltreForm(request.GET or None)
    mesures = Mesure.objects.all()

    if form.is_valid():
        nom_ou_id = form.cleaned_data.get('nom_ou_id')
        date_debut = form.cleaned_data.get('date_debut')
        date_fin = form.cleaned_data.get('date_fin')

        if nom_ou_id:
            capteurs_par_nom = Capteur.objects.filter(nom_capteur__icontains=nom_ou_id)
            capteurs_par_id = Capteur.objects.filter(id_capteur__icontains=nom_ou_id)

            ids_trouves = []
            for c in capteurs_par_nom:
                ids_trouves.append(c.id_capteur)
            for c in capteurs_par_id:
                if c.id_capteur not in ids_trouves:
                    ids_trouves.append(c.id_capteur)

            mesures = mesures.filter(id_capteur__in=ids_trouves)

        if date_debut:
            mesures = mesures.filter(timestamp_mesure__date__gte=date_debut)

        if date_fin:
            mesures = mesures.filter(timestamp_mesure__date__lte=date_fin)

    mesures = mesures.order_by('-timestamp_mesure')[:200]

    total_temperatures = 0
    nombre_de_mesures = 0
    for m in mesures:
        total_temperatures = total_temperatures + float(m.temperature)
        nombre_de_mesures = nombre_de_mesures + 1

    if nombre_de_mesures > 0:
        temp_moyenne = round(total_temperatures / nombre_de_mesures, 2)
    else:
        temp_moyenne = None

    contexte = {
        'form': form,
        'mesures': mesures,
        'temp_moyenne': temp_moyenne,
    }
    return render(request, 'capteurs/donnees.html', contexte)


def graphique(request, id_capteur):
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)
    mesures = Mesure.objects.filter(id_capteur=capteur).order_by('timestamp_mesure')[:100]

    labels = []
    valeurs = []

    for m in mesures:
        labels.append(str(m.timestamp_mesure))
        valeurs.append(float(m.temperature))

    labels_json = json.dumps(labels)
    valeurs_json = json.dumps(valeurs)

    contexte = {
        'capteur': capteur,
        'labels': labels_json,
        'valeurs': valeurs_json,
    }
    return render(request, 'capteurs/graphique.html', contexte)


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donnees_sae204.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Mesure', 'ID Capteur', 'Nom', 'Pièce', 'Timestamp', 'Temp (°C)'])

    toutes_les_mesures = Mesure.objects.all().order_by('-timestamp_mesure')

    for m in toutes_les_mesures:
        writer.writerow([
            m.id_mesure,
            m.id_capteur.id_capteur,
            m.id_capteur.nom_capteur,
            m.id_capteur.piece,
            m.timestamp_mesure,
            m.temperature,
        ])

    return response
