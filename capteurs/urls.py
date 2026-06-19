from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.liste_capteurs,    name='liste_capteurs'),
    path('capteur/<str:id_capteur>/',           views.detail_capteur,    name='detail_capteur'),
    path('capteur/<str:id_capteur>/supprimer/', views.supprimer_capteur, name='supprimer_capteur'),
    path('capteur/<str:id_capteur>/graphique/', views.graphique,         name='graphique'),
    path('donnees/',                            views.donnees,           name='donnees'),
    path('export/',                             views.export_csv,        name='export_csv'),
]