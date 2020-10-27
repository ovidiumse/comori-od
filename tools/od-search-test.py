#!/usr/bin/pypy3

import os
import argparse
import subprocess
from prettytable import PrettyTable

PARSER_ = argparse.ArgumentParser(description="OD search test.")

def parseArgs():
    PARSER_.add_argument("-o",
                         "--output",
                         dest="outdir",
                         action="store",
                         type=str,
                         required=True,
                         help="Results folder")

    return PARSER_.parse_args()


def run_searches(outdir):
    queries = [
        "Dumnezeu", "Ajutor", "Iertare", "Smerenie", "Indurare", "Îndurare",
        "Suferinta", "Suferință", "Vindecare", "Lumina", "Lumină", "Minune",
        "Jertfa", "Jertfă", "Adevar", "Adevăr", "Alinare", "Cuvant", "Cuvânt",
        "Paine", "Pâine", "Hristos", "Legamant", "Legământ", "Binefacere",
        "Invatatura", "Învățătură", "Prieten", "Botez", "Sfant", "Sfânt",
        "Duh", "Cununie", "Sfarsit", "Sfârșit", "Inceput", "Început", "Potir",
        "Biserica", "Biserică", "Bogatie", "Bogăție", "Sarac", "Sărac",
        "Popor", "Taina", "Taină", "Mangaiere", "Mângâiere", "Parinte",
        "Părinte", "Vestire", "Aflare", "Viata", "Viață", "Moarte", "Nastere",
        "Naștere", "nasterea din nou", "preinchipuit", "nesfarsit", "Frate",
        "Mama", "Tata", "Sora", "Pagan", "Credincios", "Cruce", "Golgota",
        "l-au adus la Isus", "Asternut", "Roua", "Cina", "Apa", "Pamant",
        "Sange", "Dragoste", "Iubire", "Rabdare", "Pustiu", "Inger",
        "Mantuitor", "Isus", "Ocara", "Argint", "Aur", "Lemn", "Bucurie",
        "Nadejde", "Mandrie", "Minciuna", "Batran", "Tanar", "Har", "Bun",
        "Rau", "Lacrimi", "Vesnic", "Judecata", "Nou", "Vechi", "Ascultare",
        "Maica", "Domnul", "Mire", "Mireasa", "Logodna", "Viu", "Rece",
        "Fierbinte", "Genunchi", "Curat", "Intinat", "Cer", "Intelept",
        "Intelepciune", "Ura", "Dar", "Biruinta", "Infrangere", "Neam",
        "Vrajmas", "Legat", "Legatura", "Cunostinta", "Ingamfa", "Vorbire",
        "Tacere", "Mult", "Putin", "Inchinare", "Rugaciune", "Fericit",
        "Fericire", "Aproape", "Departe", "Intuneric", "Sus", "Jos", "Sarut",
        "Inima", "Valoare", "Rasplata", "Odihna", "Inviere", "Om", "Invatator",
        "Invatatura", "Lupta", "Infrant", "Infranare", "Post", "Plans",
        "Stralucire", "Intinare", "Cantare", "Cerere", "Etern", "Legat",
        "Legatura", "Slobod", "Slobozenie", "Clocot", "Constiinta", "Cuget",
        "Gand", "Suflet", "Pace", "Razboi", "Chemare", "Vremea", "Timpul",
        "Ales", "Alegere", "Lauda", "Rusinea", "Mort", "Nor", "Soare",
        "Martor", "Marturisitor", "Lepadat", "Lepadare", "Cuviinta", "Evlavie",
        "Evlavios", "Crestin", "Ostas", "Zadarnic", "Zadarnicie", "Pierdere",
        "Pierdut", "Vina", "Vinovat", "Osanda", "Blestem", "Binecuvantare",
        "Inselat", "Inselaciune", "Dulce", "Amar", "Copil", "Slab", "Tare",
        "Slabiciune", "Unitate", "Dezbinare", "Unire", "Frica", "Despartire",
        "Curaj", "Fuga", "Flamand", "Desfranare", "Imbuibare", "Cazut",
        "Intors", "Intoarcere", "Hotarat", "Hotarare", "Meditare", "Meditatie",
        "Poezie", "Citire", "Trezire", "Rod", "Cules", "Adunare", "Altar",
        "Apus", "Rasarit", "Ridicat", "Bland", "Blandete", "Afara", "Inauntru",
        "Gol", "Acoperit", "Bolnav", "Sanatos", "Lacom", "Lacomie",
        "Predestinare", "Prooroci", "Prorocii", "Chin", "Cautare", "Ajuns",
        "Ajungere", "Plin", "Murdar", "nu esti tu la rand",
        "nu ești tu la rând"
    ]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for q in queries:
        filename = "{}.txt".format(os.path.join(outdir, q.replace(" ", "_")))
        print("Searching for '{}'".format(q))
        lines = []
        articles = []
        article = {}
        args = [
            "./od-search.py", q, "-f", "hits", "score", "volume", "book",
            "title", "type", "author", "highlight"
        ]
        with subprocess.Popen(args,
                              stdout=subprocess.PIPE,
                              universal_newlines=True) as proc:
            for line in proc.stdout:
                line = line.strip()
                if line.startswith("Score: "):
                    article = {'score': line[len("Score: "):]}
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
                elif not line and article:
                    articles.append(article)
                    article = {}

                lines.append(line)

        tbl = PrettyTable()
        tbl.field_names = ["Titlu", "Author", "Tip", "Carte", "Volum"]
        for f in tbl.field_names:
            tbl.align[f] = 'l'

        articles = sorted(articles, key=lambda a: a['score'], reverse=True)
        for article in articles:
            tbl.add_row([
                article['title'], article['author'], article['book'],
                article['volume'], article['type']
            ])

        with open(filename, 'w') as out_file:
            print(tbl, file=out_file)
            for line in lines:
                print(line, file=out_file)



def main():
    args = parseArgs()

    run_searches(args.outdir)

if __name__ == "__main__":
    main()