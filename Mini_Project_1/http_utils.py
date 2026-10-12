from threading import *

#Dico pour cache
cache_http = {}
verrou = Lock()



# Fonction pour ecrire dans le cache avec des verrous
def cache_put(cle, valeur):
    """Écrit ou met à jour une entrée dans le dictionnaire de manière thread-safe."""
    with verrou:
        cache_http[cle] = valeur


def cache_read(cle, valeur_defaut=None):
    """Lit une valeur dans le dictionnaire de manière thread-safe.
    Renvoie valeur_defaut si la clé n'existe pas.
    """
    with verrou:
        return cache_http.get(cle, valeur_defaut)


def read_request(socket):
    buffer = b""
    
    # On lit uniquement jusqu'à la fin des en-têtes
    while b"\r\n\r\n" not in buffer:
        message = socket.recv(4028)
        if not message:
            raise ConnectionError("La connexion a ete interrompue !")
        buffer = buffer + message
    return buffer

def read_response(socket):
    buffer = b""
    buffer_core = b""
    taille = 0

    # On recupere l'entete
    while b"\r\n\r\n" not in buffer:
        message = socket.recv(4028)
        if not message:
            raise ConnectionError("La connexion a ete interrompue !")
        
        buffer = buffer + message
    en_tete, corps = buffer.split(b"\r\n\r\n", 1)
    buffer = en_tete

    # On recupere juste le corps
    buffer_core = buffer_core + corps

    en_tete_split = en_tete.split(b"\r\n")

    # On parcour lentete
    for ligne in en_tete_split:
        if b"content-length" in ligne.lower():
            ligne_length = ligne.split(b":")
            taille = int(ligne_length[1])

    if taille == 0:
        return buffer + b"\r\n\r\n"

    # On recupere tout le messages
    while len(buffer_core) < taille:
        message = socket.recv(4028)
        if not message:
            raise ConnectionError("La connexion a ete interrompue !")
        
        buffer_core = buffer_core + message

    buffer = buffer + b"\r\n\r\n" + buffer_core

    return buffer







def parse_request(data):
    # On sépare les en-têtes du reste de la requête
    lignes = data.decode("utf-8").split("\r\n")

    # Première ligne : méthode, URI et version HTTP
    method, uri, version = lignes[0].split(" ", 2)

    # Dictionnaire des en-têtes
    headers = {}

    for ligne in lignes[1:]:
        if ligne == "":
            break

        nom, valeur = ligne.split(":", 1)
        headers[nom.strip().lower()] = valeur.strip()

    return method, uri, version, headers

def split_response(data):
    # Séparer les en-têtes du corps
    tete, body = data.split(b"\r\n\r\n", 1)

    # Lire la ligne de statut
    lignes = tete.decode("utf-8").split("\r\n")
    premiere_ligne = lignes[0]

    # Exemple : HTTP/1.1 200 OK
    version, status, *raison = premiere_ligne.split(" ")

    status = int(status)

    # Lire les en-têtes
    headers = {}

    for ligne in lignes[1:]:
        nom, valeur = ligne.split(":", 1)
        headers[nom.strip().lower()] = valeur.strip()

    return status, headers, body


def build_request(method, url, version, headers):


    nouveaux_headers = {}

    for cle, valeur in headers.items():
        if cle.lower() != "connection" and cle.lower() != "accept-encoding":
            nouveaux_headers[cle] = valeur

    nouveaux_headers["Connection"] = "close"

    request = f"{method} {url} {version}\r\n"

    for cle, valeur in nouveaux_headers.items():
        request = request + f"{cle}: {valeur}\r\n"

    request = request + "\r\n"

    return request.encode("utf-8")


def build_response(status, reason, body, content_type):

    response =(
                f"HTTP/1.1 {status} {reason}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n\r\n")
                

    return  response.encode("utf-8") + body