import argparse

def search_log(fichier, uri):

    Ip = set()

    
    with open(fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            elem = ligne.rstrip("\n").split("\t")

            # a valid log line has 7 columns:
            # timestamp, id, type, client ip, uri, status, body size
            if len(elem) != 7:
                continue

            # look at the type column and the uri column only
            if elem[2] == "RESPONSE" and uri in elem[4]:
                try:
                    # only count non-empty responses
                    if int(elem[6]) > 0:
                        Ip.add(elem[3])
                except ValueError:
                    continue

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

    for ip in sorted(Ip):
        print(f"IP client that received response for URI {uri} : {ip}")


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