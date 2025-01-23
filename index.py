import requests

# Informations nécessaires pour la connexion
API_URL = "http://localhost/apirest.php/"
APP_TOKEN = "MT76sMEzOfX6gz6zq6E66ZM9DOcoCtOwC4PaoerC"  # Token d'application généré dans GLPI
USER_TOKEN = "bBACPqvhiEmllVpxJrXgKTfILYR8CKk8sHU0XqLF"  # Token d'utilisateur généré dans GLPI

# Headers pour l'authentification
headers = {
    "Content-Type": "application/json",
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}"
}

try:
    # Test de connexion : Récupérer la version de GLPI
    response = requests.get(f"{API_URL}/initSession", headers=headers)

    if response.status_code == 200:
        print("Connexion établie avec succès !")
        print("Version de GLPI :", response.json().get("glpi_version", "Version inconnue"))
    else:
        print(f"Erreur lors de la connexion : {response.status_code}")
        print("Détails :", response.text)

except Exception as e:
    print("Une erreur est survenue :", str(e))
