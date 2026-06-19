from django.db import models


# ---------------------------------------------------------------------------
# Ce fichier décrit la "forme" des données stockées dans la base MySQL.
# Chaque classe = une table. Chaque attribut = une colonne.
# ---------------------------------------------------------------------------


# Table "capteurs" : un capteur = un appareil qui mesure la température
class Capteur(models.Model):
    # Identifiant unique du capteur (ex : son adresse MAC). C'est la clé primaire.
    id_capteur = models.CharField(max_length=50, primary_key=True)

    # Le "petit nom" du capteur, modifiable plus tard depuis le site web.
    # unique=True : deux capteurs ne peuvent pas avoir le même nom.
    nom_capteur = models.CharField(max_length=100, unique=True, default='Capteur_Inconnu')

    # La pièce où se trouve le capteur. Cette info vient du message MQTT, on ne la modifie pas ici.
    piece = models.CharField(max_length=100)

    # L'emplacement précis (texte libre), modifiable depuis le site web.
    emplacement = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'capteurs'  # nom exact de la table dans MySQL
        managed = False        # la table existe déjà (créée par notre script SQL),
        # donc on dit à Django : "ne touche pas à la structure de cette table"

    def __str__(self):
        # Ce texte s'affiche quand on imprime un objet Capteur (utile pour déboguer)
        return f"{self.nom_capteur} ({self.id_capteur})"


# Table "mesures" : une ligne = une mesure de température prise à un instant donné
class Mesure(models.Model):
    # Identifiant auto-incrémenté de la mesure (1, 2, 3, ...)
    id_mesure = models.AutoField(primary_key=True)

    # Clé étrangère vers le capteur qui a fait cette mesure.
    # on_delete=CASCADE : si on supprime le capteur, ses mesures sont supprimées aussi.
    id_capteur = models.ForeignKey(
        Capteur,
        on_delete=models.CASCADE,
        db_column='id_capteur'
    )

    # Date et heure de la mesure
    timestamp_mesure = models.DateTimeField()

    # La température mesurée (ex : 21.50)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'mesures'
        managed = False
        ordering = ['-timestamp_mesure']  # par défaut : les mesures les plus récentes d'abord

    def __str__(self):
        return f"{self.id_capteur_id} — {self.temperature}°C"
