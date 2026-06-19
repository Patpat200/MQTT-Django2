from django.db import models


class Capteur(models.Model):
    id_capteur = models.CharField(max_length=50, primary_key=True)
    nom_capteur = models.CharField(max_length=100, unique=True, default='Capteur_Inconnu')
    piece = models.CharField(max_length=100)
    emplacement = models.CharField(max_length=100, blank=True, default='')
    
    class Meta:
        db_table = 'capteurs'
        managed = False

    def __str__(self):
        return f"{self.nom_capteur} ({self.id_capteur})"


class Mesure(models.Model):
    id_mesure = models.AutoField(primary_key=True)
    id_capteur = models.ForeignKey(
        Capteur,
        on_delete=models.CASCADE,
        db_column='id_capteur'
    )
    timestamp_mesure = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'mesures'
        managed = False
        ordering = ['-timestamp_mesure']

    def __str__(self):
        return f"{self.id_capteur_id} — {self.temperature}°C"
