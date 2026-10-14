from threading import *
from pathlib import Path
import re
#Dico pour cache,log
cache_http = {}
verrou = Lock()
log_lock = Lock()






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
   
    buffer = b''

    while True:
       message = socket.recv(4096)
       if message == b'':
           break
       buffer += message

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


def clean_field(field):
    return str(field).replace("\n", " ").replace("\r", " ").replace("\t", " ")

# Fonction pour ecrire dans le log
def write_log(fichier, log):
    
    try:
        fichier = Path(fichier)
        fichier.parent.mkdir(parents=True, exist_ok=True)
        with log_lock:
            with open(fichier, "a",encoding="utf-8") as f:
                f.write(log + "\n")
    except OSError as e:
        print(f"error while writing to the log file: {e}")

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


def load_banned_sites(bannedURI):
    try:
        with open(bannedURI, "r", encoding="utf-8") as f:
            return [
                line.strip().lower()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
    except FileNotFoundError:
        print(f"Error: banned URI file '{bannedURI}' does not exist.")
        return []
    except OSError as e:
        print(f"Error while opening banned URI file '{bannedURI}': {e}")
        return []



def censor_response(response, banned_sites):
    head, body = response.split(b"\r\n\r\n", 1)
    censored = False

    for site in banned_sites:
        pattern = (
            rb'<a\b[^>]*href\s*=\s*["\'][^"\']*'
            + re.escape(site.encode("utf-8"))
            + rb'[^"\']*["\'][^>]*>.*?</a\s*>'
        )

        body, count = re.subn(
            pattern, b"Forbidden", body,
            flags=re.IGNORECASE | re.DOTALL
        )
        censored = censored or count > 0

    if not censored:
        return response, False

    headers = head.split(b"\r\n")
    headers = [
        line for line in headers
        if not line.lower().startswith(b"content-length:")
    ]
    headers.append(f"Content-Length: {len(body)}".encode())

    return b"\r\n".join(headers) + b"\r\n\r\n" + body, True