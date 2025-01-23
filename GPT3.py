import requests
from datetime import datetime
from gpt4all import GPT4All

# Configuration de l'API GLPI
GLPI_URL = "http://192.168.174.129/glpi/apirest.php"
APP_TOKEN = "v3hncubzZU8N2vrnw3nQhl8ItFon2PhwEvFV9wSD"
USER_TOKEN = "b5Qn42Y7pzjfIg8WiZPYakGkVKl0kbsG301Ey6FX"

# En-têtes pour l'authentification
headers = {
    "Authorization": f"user_token {USER_TOKEN}",
    "App-Token": APP_TOKEN
}

# Fonction pour afficher l'heure actuelle
def print_execution_time(step=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{step} - Exécution à : {now}")

# Fonction pour ouvrir une session dans GLPI
def init_session():
    print_execution_time("Initialisation de la session")
    try:
        response = requests.get(f"{GLPI_URL}/initSession", headers=headers)
        if response.status_code == 200:
            session_token = response.json()["session_token"]
            print("Session initialisée avec succès.")
            return session_token
        else:
            print(f"Erreur d'initialisation de la session : {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Erreur : {e}")
        return None

# Fonction pour récupérer les tickets
def get_tickets(session_token):
    print_execution_time("Récupération des tickets")
    try:
        session_headers = headers.copy()
        session_headers["Session-Token"] = session_token
        response = requests.get(f"{GLPI_URL}/Ticket", headers=session_headers)
        if response.status_code == 200:
            tickets = response.json()
            print("Liste des tickets récupérée avec succès.")
            return tickets
        else:
            print(f"Erreur lors de la récupération des tickets : {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Erreur : {e}")
        return None

# Fonction pour mettre à jour le statut d'un ticket
def update_ticket_status(session_token, ticket_id, new_status):
    try:
        session_headers = headers.copy()
        session_headers["Session-Token"] = session_token
        data = {
            "input": {
                "id": ticket_id,
                "status": new_status
            }
        }
        response = requests.put(f"{GLPI_URL}/Ticket/{ticket_id}", headers=session_headers, json=data)
        if response.status_code == 200:
            print(f"Ticket modifié : ID {ticket_id}, nouveau statut : {new_status}")
        else:
            print(f"Erreur lors de la mise à jour du ticket ID {ticket_id} : {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erreur : {e}")

# Fonction pour ajouter un suivi (message) à un ticket en utilisant GPT4All
def add_ticket_followup(session_token, ticket_id, content):
    try:
        session_headers = headers.copy()
        session_headers["Session-Token"] = session_token
        
        # Initialiser le modèle GPT4All
        model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
        with model.chat_session() as session:
            ai_response = session.generate(content, max_tokens=200)
        
        data = {
            "input": {
                "tickets_id": ticket_id,
                "content": ai_response
            }
        }
        response = requests.post(f"{GLPI_URL}/Ticket/{ticket_id}/TicketFollowup", headers=session_headers, json=data)
        if response.status_code in [200, 201]:
            print(f"Message ajouté au ticket ID {ticket_id} : {ai_response}")
        else:
            print(f"Erreur lors de l'ajout du message au ticket ID {ticket_id} : {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erreur : {e}")

# Fonction pour fermer la session
def kill_session(session_token):
    print_execution_time("Fermeture de la session")
    try:
        session_headers = headers.copy()
        session_headers["Session-Token"] = session_token
        response = requests.get(f"{GLPI_URL}/killSession", headers=session_headers)
        if response.status_code == 200:
            print("Session terminée avec succès.")
        else:
            print(f"Erreur lors de la fermeture de la session : {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erreur : {e}")

# Script principal
if __name__ == "__main__":
    print("#" * 50)
    print_execution_time("Début du script")
    print("#" * 50)

    session_token = init_session()
    if session_token:
        tickets = get_tickets(session_token)
        if tickets:
            print("\nTickets avec statut 'Nouveau' :")
            for ticket in tickets:
                if ticket.get("status", "Inconnu") == 1:  # Statut "Nouveau"
                    ticket_id = ticket.get("id", "Inconnu")
                    ticket_name = ticket.get("name", "Inconnu")
                    print(f"ID: {ticket_id}, Titre: {ticket_name}, Statut: Nouveau")
                    
                    # Mettre à jour le statut du ticket
                    update_ticket_status(session_token, ticket_id, new_status=2)
                    
                    # Ajouter un suivi avec une réponse générée par AI
                    message = f"Le ticket '{ticket_name}' a été pris en charge et est maintenant en cours de traitement. Voici une réponse automatique :"
                    add_ticket_followup(session_token, ticket_id, message)

        # Fermer la session
        kill_session(session_token)

    print("#" * 50)
    print_execution_time("Fin du script")
    print("#" * 50)