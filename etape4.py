import requests

# Informations nécessaires pour la connexion
API_URL = "http://localhost/apirest.php/"
APP_TOKEN = "MT76sMEzOfX6gz6zq6E66ZM9DOcoCtOwC4PaoerC"  # Token d'application généré dans GLPI
USER_TOKEN = "bBACPqvhiEmllVpxJrXgKTfILYR8CKk8sHU0XqLF"  # Token d'utilisateur généré dans GLPI

# Headers pour initSession
auth_headers = {
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}"
}

try:
    # 1. Ouvrir une session
    session_response = requests.get(f"{API_URL}/initSession", headers=auth_headers)

    if session_response.status_code == 200:
        session_data = session_response.json()
        session_token = session_data["session_token"]
        print("Session ouverte avec succès. Session Token :", session_token)

        # Ajouter le session_token aux headers pour les prochaines requêtes
        headers = {
            "App-Token": APP_TOKEN,
            "Session-Token": session_token
        }

        # 2. Récupérer tous les tickets
        response = requests.get(f"{API_URL}/Ticket", headers=headers)

        if response.status_code == 200:
            tickets = response.json()

            # Filtrer les tickets avec le statut "Nouveau" (par exemple, statut ID = 3)
            status_id_new = 1  # ID pour "Nouveau"
            status_id_in_progress = 2  # ID pour "En cours"
            filtered_tickets = [
                ticket for ticket in tickets if ticket.get("status") == status_id_new
            ]

            print("Tickets avec le statut 'Nouveau' :")
            for ticket in filtered_tickets:
                print(f"ID: {ticket['id']}, Titre: {ticket['name']}, Statut: {ticket['status']}")

                # 3. Ajouter un suivi à chaque ticket
                followup_data = {
                    "input": {
                        "itemtype": "Ticket",
                        "items_id": ticket['id'],
                        "content": "Traitement pris en charge par nos services."
                    }
                }

                followup_response = requests.post(
                    f"{API_URL}/Ticket/{ticket['id']}/ITILFollowup",
                    headers=headers,
                    json=followup_data
                )

                if followup_response.status_code == 201:
                    print(f"Suivi ajouté au ticket ID: {ticket['id']}")

                    # 4. Mettre à jour le statut du ticket à "En cours"
                    update_data = {
                        "input": {
                            "id": ticket['id'],
                            "status": status_id_in_progress
                        }
                    }

                    update_response = requests.put(
                        f"{API_URL}/Ticket/{ticket['id']}",
                        headers=headers,
                        json=update_data
                    )

                    if update_response.status_code == 200:
                        print(f"Statut du ticket ID {ticket['id']} mis à jour à 'En cours'.")
                    else:
                        print(f"Erreur lors de la mise à jour du statut du ticket ID: {ticket['id']}")
                        print("Détails :", update_response.text)
                else:
                    print(f"Erreur lors de l'ajout du suivi au ticket ID: {ticket['id']}")
                    print("Détails :", followup_response.text)

        else:
            print(f"Erreur lors de la récupération des tickets : {response.status_code}")
            print("Détails :", response.text)

        # 5. Fermer la session (important)
        requests.get(f"{API_URL}/killSession", headers=headers)

    else:
        print(f"Erreur lors de l'ouverture de la session : {session_response.status_code}")
        print("Détails :", session_response.text)

except Exception as e:
    print("Une erreur est survenue :", str(e))

