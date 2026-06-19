from django import forms
from .models import Capteur


class CapteurEditForm(forms.ModelForm):
    class Meta:
        model  = Capteur
        fields = ['nom_capteur', 'emplacement']   # seuls champs modifiables
        widgets = {
            'nom_capteur': forms.TextInput(attrs={'class': 'form-control'}),
            'emplacement': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FiltreForm(forms.Form):
    nom_ou_id  = forms.CharField(
        required=False,
        label="Nom ou ID du capteur",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex: 12A6B8 ou Capteur1'
        })
    )
    date_debut = forms.DateField(
        required=False,
        label="Date de début",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin   = forms.DateField(
        required=False,
        label="Date de fin",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )