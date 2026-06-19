import json
import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from .models import Capteur, Mesure
from .forms import CapteurEditForm, FiltreForm


# ===========================================================================
# Ce fichier contient une fonction par page du site.
# Chaque fonction reçoit la "requête" (request) envoyée par le navigateur,
# va chercher les informations dans la base de données,
# puis renvoie une page HTML construite à partir d'un template.
# ===========================================================================


# ---------------------------------------------------------------------------
# Page d'accueil : liste de tous les capteurs connus
# ---------------------------------------------------------------------------
def liste_capteurs(request):
    # On récupère tous les capteurs enregistrés dans la base
    capteurs = Capteur.objects.all()

    # On envoie cette liste au template, qui va l'afficher dans un tableau
    return render(request, 'capteurs/liste_capteurs.html', {'capteurs': capteurs})


# ---------------------------------------------------------------------------
# Page de détail d'un capteur : ses infos, son formulaire de modification,
# et ses 50 dernières mesures
# ---------------------------------------------------------------------------
def detail_capteur(request, id_capteur):
    # On va chercher le capteur demandé. S'il n'existe pas, Django affiche
    # automatiquement une page d'erreur 404 (page non trouvée).
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)

    if request.method == 'POST':
        # L'utilisateur a cliqué sur "Enregistrer" : on récupère les données du formulaire
        form = CapteurEditForm(request.POST, instance=capteur)
        if form.is_valid():
            form.save()  # on enregistre les changements en base de données
            # On recharge la page pour voir les changements
            return redirect('detail_capteur', id_capteur=id_capteur)
    else:
        # Premier affichage de la page : on pré-remplit le formulaire avec les valeurs actuelles
        form = CapteurEditForm(instance=capteur)

    # On récupère les 50 dernières mesures de ce capteur, triées de la plus récente à la plus ancienne
    mesures = Mesure.objects.filter(id_capteur=capteur).order_by('-timestamp_mesure')[:50]

    contexte = {
        'capteur': capteur,
        'form': form,
        'mesures': mesures,
    }
    return render(request, 'capteurs/detail_capteur.html', contexte)


# ---------------------------------------------------------------------------
# Suppression d'un capteur (avec une page de confirmation avant)
# ---------------------------------------------------------------------------
def supprimer_capteur(request, id_capteur):
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)

    if request.method == 'POST':
        # L'utilisateur a cliqué sur "Confirmer" : on supprime pour de vrai.
        # Comme on a mis on_delete=CASCADE dans le modèle Mesure, toutes les
        # mesures liées à ce capteur seront supprimées automatiquement aussi.
        capteur.delete()
        return redirect('liste_capteurs')

    # Si on arrive ici, c'est juste pour afficher la page "Es-tu sûr ?"
    return render(request, 'capteurs/confirmer_suppression.html', {'capteur': capteur})


# ---------------------------------------------------------------------------
# Page "Données" : tableau de toutes les mesures, avec filtres cumulables
# ---------------------------------------------------------------------------
def donnees(request):
    # request.GET contient les paramètres tapés dans le formulaire (méthode GET).
    # Si l'utilisateur n'a encore rien rempli, request.GET est vide, donc on
    # passe None au formulaire (= formulaire vide, pas encore validé).
    form = FiltreForm(request.GET or None)

    # On part de TOUTES les mesures, puis on va retirer celles qui ne correspondent
    # pas aux filtres demandés, petit à petit.
    mesures = Mesure.objects.all()

    if form.is_valid():
        nom_ou_id = form.cleaned_data.get('nom_ou_id')
        date_debut = form.cleaned_data.get('date_debut')
        date_fin = form.cleaned_data.get('date_fin')

        # --- Filtre 1 : recherche par nom OU par identifiant de capteur ---
        if nom_ou_id:
            # On cherche d'abord la liste des capteurs qui correspondent,
            # soit par leur nom, soit par leur identifiant.
            capteurs_par_nom = Capteur.objects.filter(nom_capteur__icontains=nom_ou_id)
            capteurs_par_id = Capteur.objects.filter(id_capteur__icontains=nom_ou_id)

            # On construit une liste (sans doublons) des identifiants trouvés
            ids_trouves = []
            for c in capteurs_par_nom:
                ids_trouves.append(c.id_capteur)
            for c in capteurs_par_id:
                if c.id_capteur not in ids_trouves:
                    ids_trouves.append(c.id_capteur)

            # On garde seulement les mesures qui appartiennent à un de ces capteurs
            mesures = mesures.filter(id_capteur__in=ids_trouves)

        # --- Filtre 2 : à partir d'une date de début ---
        if date_debut:
            mesures = mesures.filter(timestamp_mesure__date__gte=date_debut)

        # --- Filtre 3 : jusqu'à une date de fin ---
        if date_fin:
            mesures = mesures.filter(timestamp_mesure__date__lte=date_fin)

    # On trie du plus récent au plus ancien, et on limite l'affichage à 200 lignes
    # (pour ne pas surcharger la page si la base contient des milliers de mesures)
    mesures = mesures.order_by('-timestamp_mesure')[:200]

    # --- Calcul de la température moyenne "à la main", sans fonction magique ---
    total_temperatures = 0
    nombre_de_mesures = 0
    for m in mesures:
        total_temperatures = total_temperatures + float(m.temperature)
        nombre_de_mesures = nombre_de_mesures + 1

    if nombre_de_mesures > 0:
        temp_moyenne = round(total_temperatures / nombre_de_mesures, 2)
    else:
        temp_moyenne = None  # pas de mesures => pas de moyenne à afficher

    contexte = {
        'form': form,
        'mesures': mesures,
        'temp_moyenne': temp_moyenne,
    }
    return render(request, 'capteurs/donnees.html', contexte)


# ---------------------------------------------------------------------------
# Page "Graphique" : courbe de température d'un capteur avec Chart.js
# ---------------------------------------------------------------------------
def graphique(request, id_capteur):
    # 1) On récupère le capteur concerné
    capteur = get_object_or_404(Capteur, id_capteur=id_capteur)

    # 2) On récupère ses 100 dernières mesures, triées de la plus ANCIENNE
    #    à la plus RÉCENTE (important pour qu'une courbe se lise de gauche à droite !)
    mesures = Mesure.objects.filter(id_capteur=capteur).order_by('timestamp_mesure')[:100]

    # 3) Un graphique Chart.js a besoin de deux listes simples :
    #       labels  -> ce qui sera affiché sur l'axe horizontal (les dates/heures)
    #       valeurs -> ce qui sera affiché sur l'axe vertical   (les températures)
    labels = []
    valeurs = []

    # On parcourt chaque mesure une par une, et on ajoute ses infos dans les deux listes
    for m in mesures:
        labels.append(str(m.timestamp_mesure))   # ex: "2026-06-19 10:05:00"
        valeurs.append(float(m.temperature))      # ex: 21.5

    # 4) Les listes Python ne peuvent pas être lues directement par JavaScript.
    #    json.dumps() les transforme en texte au format JSON, par exemple :
    #       ["2026-06-19 10:05:00", "2026-06-19 10:10:00"]  ->  texte JSON
    #    Ce texte sera ensuite collé dans le <script> du template HTML.
    labels_json = json.dumps(labels)
    valeurs_json = json.dumps(valeurs)

    contexte = {
        'capteur': capteur,
        'labels': labels_json,
        'valeurs': valeurs_json,
    }
    return render(request, 'capteurs/graphique.html', contexte)


# ---------------------------------------------------------------------------
# Export de toutes les mesures au format CSV (ouvrable dans Excel)
# ---------------------------------------------------------------------------
def export_csv(request):
    # On prépare une réponse HTTP qui sera comprise par le navigateur comme
    # un fichier à télécharger, et non comme une page web normale.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donnees_sae204.csv"'

    # csv.writer sait écrire des lignes au bon format (avec virgules, guillemets, etc.)
    writer = csv.writer(response)

    # Première ligne du fichier : les titres de colonnes
    writer.writerow(['ID Mesure', 'ID Capteur', 'Nom', 'Pièce', 'Timestamp', 'Temp (°C)'])

    # On récupère toutes les mesures, les plus récentes en premier
    toutes_les_mesures = Mesure.objects.all().order_by('-timestamp_mesure')

    # On écrit une ligne de CSV par mesure
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
