from django.urls import path
from . import views

# ---------------------------------------------------------------------------
# Ce fichier fait le lien entre une adresse tapée dans le navigateur (URL)
# et la fonction Python (dans views.py) qui doit répondre.
# ---------------------------------------------------------------------------

urlpatterns = [
    # http://.../                                -> page d'accueil (liste des capteurs)
    path('', views.liste_capteurs, name='liste_capteurs'),

    # http://.../capteur/<id>/                    -> détail d'un capteur
    path('capteur/<str:id_capteur>/', views.detail_capteur, name='detail_capteur'),

    # http://.../capteur/<id>/supprimer/           -> confirmation puis suppression
    path('capteur/<str:id_capteur>/supprimer/', views.supprimer_capteur, name='supprimer_capteur'),

    # http://.../capteur/<id>/graphique/           -> courbe de température du capteur
    path('capteur/<str:id_capteur>/graphique/', views.graphique, name='graphique'),

    # http://.../donnees/                          -> tableau de toutes les mesures + filtres
    path('donnees/', views.donnees, name='donnees'),

    # http://.../export/                           -> téléchargement du fichier CSV
    path('export/', views.export_csv, name='export_csv'),
]
