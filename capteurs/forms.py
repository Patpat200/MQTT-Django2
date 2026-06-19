from django import forms
from .models import Capteur


# ---------------------------------------------------------------------------
# Ce fichier décrit les formulaires affichés sur le site.
# Un formulaire Django sait : afficher les champs en HTML, ET vérifier
# que ce que l'utilisateur a tapé est valide.
# ---------------------------------------------------------------------------


# Formulaire utilisé sur la page "détail d'un capteur" pour le modifier.
# On limite volontairement les champs modifiables à nom_capteur et emplacement,
# car l'id_capteur et la piece ne doivent pas pouvoir être changés depuis le site.
class CapteurEditForm(forms.ModelForm):
    class Meta:
        model = Capteur
        fields = ['nom_capteur', 'emplacement']
        widgets = {
            'nom_capteur': forms.TextInput(attrs={'class': 'form-control'}),
            'emplacement': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Formulaire utilisé sur la page "Données" pour filtrer les résultats.
# Tous les champs sont "required=False" car on veut pouvoir afficher
# toutes les données si l'utilisateur ne remplit rien.
class FiltreForm(forms.Form):

    # On cherchera un capteur soit par son nom, soit par son identifiant
    nom_ou_id = forms.CharField(
        required=False,
        label="Nom ou ID du capteur",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex: 12A6B8 ou Capteur1'
        })
    )

    # Filtre optionnel : ne garder que les mesures à partir de cette date
    date_debut = forms.DateField(
        required=False,
        label="Date de début",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    # Filtre optionnel : ne garder que les mesures jusqu'à cette date
    date_fin = forms.DateField(
        required=False,
        label="Date de fin",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
