from django.contrib import admin
from django.urls import path, include

# urls.py "principal" du projet : il redirige simplement tout le trafic
# (sauf /admin/) vers les URLs définies dans l'app capteurs.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('capteurs.urls')),
]
