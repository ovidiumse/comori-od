#!/usr/bin/pypy3

import os
import argparse
import subprocess
from prettytable import PrettyTable

PARSER_ = argparse.ArgumentParser(description="OD search test.")

def parseArgs():
    PARSER_.add_argument("-i",
                         "--index-name",
                         action="store",
                         dest="idx_name",
                         default="od",
                         help="Index name")

    PARSER_.add_argument("-o",
                         "--output",
                         dest="outdir",
                         action="store",
                         type=str,
                         required=True,
                         help="Results folder")
    PARSER_.add_argument("-e", "--external-host", action="store_true", help="Query external host")
    PARSER_.add_argument("-t", "--test-host", action="store_true", help="Query test host")

    return PARSER_.parse_args()


def extract_occurrences(highlights):
    occurrences = []
    for highlight in highlights:
        end = 0
        while True:
            start = highlight.find("<em>", end)
            if start < 0:
                break
            start += len("<em>")

            end = highlight.find("</em>", start)
            if end < 0:
                break;

            occurrences.append(highlight[start:end])
            end += len("</em>")

    return set(occurrences)

def run_searches(outdir, external_host, test_host):
    queries = [
        "Dumnezeu", "Ajutor", "Iertare", "Smerenie", "Indurare", "Suferinta",
        "Vindecare", "Lumina", "Minune", "Jertfa", "Adevar", "Alinare",
        "Cuvant", "Paine", "Hristos", "Legamant", "Binefacere", "Invatatura",
        "Prieten", "Botez", "Sfant", "Duh", "Cununie", "Sfarsit", "Inceput",
        "Potir", "Biserica", "Bogatie", "Sarac", "Popor", "Taina", "Mangaiere",
        "Parinte", "Vestire", "Aflare", "Viata", "Moarte", "Nastere", "Frate",
        "Mama", "Tata", "Sora", "Pagan", "Credincios", "Cruce", "Golgota",
        "Asternut", "Roua", "Cina", "Apa", "Pamant", "Sange", "Dragoste",
        "Iubire", "Rabdare", "Pustiu", "Inger", "Mantuitor", "Isus", "Ocara",
        "Argint", "Aur", "Lemn", "Bucurie", "Nadejde", "Mandrie", "Minciuna",
        "Batran", "Tanar", "Har", "Bun", "Rau", "Lacrimi", "Vesnic",
        "Judecata", "Nou", "Vechi", "Ascultare", "Maica", "Domnul", "Mire",
        "Mireasa", "Logodna", "Viu", "Rece", "Fierbinte", "Genunchi", "Curat",
        "Intinat", "întinat", "Cer", "Intelept", "Intelepciune", "Ura", "Dar", "Biruinta",
        "Infrangere", "Neam", "Vrajmas", "Legat", "Legatura", "Cunostinta",
        "Ingamfa", "Vorbire", "Tacere", "Mult", "Putin", "Inchinare",
        "Rugaciune", "Fericit", "Fericire", "Aproape", "Departe", "Intuneric",
        "Sus", "Jos", "Sarut", "Inima", "Valoare", "Rasplata", "Odihna",
        "Inviere", "Omul", "Invatator", "Invatatura", "Lupta", "Infrant",
        "Infranare", "Post", "Plans", "Stralucire", "Intinare", "Cantare",
        "Cerere", "Etern", "Legat", "Legatura", "Slobod", "Slobozenie",
        "Clocot", "Constiinta", "Cuget", "Gand", "Suflet", "Pace", "Razboi",
        "Chemare", "Vremea", "Timpul", "Ales", "Alegere", "Lauda", "Rusinea",
        "Mort", "Nor", "Soare", "Martor", "Marturisitor", "Lepadat",
        "Lepadare", "Cuviinta", "Evlavie", "Evlavios", "Crestin", "Ostas",
        "Zadarnic", "Zadarnicie", "Pierdere", "Pierdut", "Vina", "Vinovat",
        "Osanda", "Blestem", "Binecuvantare", "Inselat", "Inselaciune",
        "Dulce", "Amar", "Copil", "Slab", "Tare", "Slabiciune", "Unitate",
        "Dezbinare", "Unire", "Frica", "Despartire", "Curaj", "Fuga",
        "Flamand", "Desfranare", "Imbuibare", "Cazut", "Intors", "Intoarcere",
        "Hotarat", "Hotarare", "Meditare", "Meditatie", "Poezie", "Citire",
        "Trezire", "Rod", "Cules", "Adunare", "Altar", "Apus", "Rasarit",
        "Ridicat", "Bland", "Blandete", "Afara", "Inauntru", "Gol", "Acoperit",
        "Bolnav", "Sanatos", "Lacom", "Lacomie", "Predestinare", "Predestinatie", "predestinație", "Prooroci",
        "Prorocii", "Chin", "Cautare", "Ajuns", "Ajungere", "Plin", "Murdar",
        "Supus", "Supunere", "femeie de ce plangi", "nu esti tu la rand", "nu ești tu la rând"
    ]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for q in sorted(queries):
        filename = "{}.txt".format(os.path.join(outdir, q.replace(" ", "_")))
        print("Searching for '{}'".format(q))
        lines = []
        articles = []
        article = {}
        args = ["./od-search.py", q]

        if external_host:
            args.append("--external-host")
        elif test_host:
            args.append("--test-host")

        args += [
            "-f", "hits", "score", "volume", "book", "title", "type", "author",
            "highlight"
        ]

        with subprocess.Popen(args,
                              stdout=subprocess.PIPE,
                              universal_newlines=True) as proc:
            for line in proc.stdout:
                line = line.strip()
                if line.startswith("Score: "):
                    article = {'score': line[len("Score: "):], 'highlights': []}
                elif line.startswith("Title: "):
                    article['title'] = line[len("Title: "):]
                elif line.startswith("Author: "):
                    article['author'] = line[len("Author: "):]
                elif line.startswith("Book: "):
                    article['book'] = line[len("Book: "):]
                elif line.startswith("Volume: "):
                    article['volume'] = line[len("Volume: "):]
                elif line.startswith("Type: "):
                    article['type'] = line[len("Type: "):]
                elif line.startswith("Highlight: "):
                    article['highlights'].append(line[len("Highlight: "):])
                elif not line and article:
                    articles.append(article)
                    article = {}

                lines.append(line)

        tbl = PrettyTable()
        tbl.field_names = ["Titlu", "Occurrences", "Author", "Tip", "Carte", "Volum"]
        for f in tbl.field_names:
            tbl.align[f] = 'l'

        for article in articles:
            tbl.add_row([
                article['title'],
                extract_occurrences(article['highlights']), article['author'],
                article['book'], article['volume'], article['type']
            ])

        with open(filename, 'w') as out_file:
            print(tbl, file=out_file)
            for line in lines:
                print(line, file=out_file)



def main():
    args = parseArgs()

    run_searches(args.outdir, args.external_host, args.test_host)

if __name__ == "__main__":
    main()