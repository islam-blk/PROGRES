import argparse

def search_log(fichier, uri):

    Ip = set()

    
    with open(fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            if "RESPONSE" in ligne and uri in ligne:
                elem = ligne.strip().split("\t")
                Ip.add(elem[3])

    return Ip

def run(fichier, uri):

    try:
        Ip = search_log(fichier, uri)
    except FileNotFoundError:
        print(f"Error: the file {fichier} does not exist.")
        return

    if len(Ip) == 0:
        print("No IP found")
        return

    for ip in Ip:
        print(f"IP client that recevied response for URI {uri} : {ip}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--uri", required=True)

    args = parser.parse_args()

    fichier = args.file
    uri = args.uri

    run(fichier, uri)


if __name__ == "__main__":
    main()