from datetime import datetime, timedelta
from datetime import date
from os import path, makedirs, remove, rename
from csv import DictWriter as csvDictWriter
from csv import DictReader as csvDictReader

delimiter = ";"

def logText(message, dossier="log"):
    nom_fichier = create_file_and_folder(dossier)
    with open(nom_fichier, 'a', encoding='utf-8') as f:
        heure = datetime.now().strftime("%H:%M:%S")
        jour = datetime.now().strftime("%d/%m/%Y")
        f.write(jour + delimiter + heure + delimiter + message + "\n")


def logCSV(*dictionaries, dossier="log"):
    """Takes one or several dictionaries as input, and logs all of its data in a CSV file.
    The header of the file is automatically updated, based on the keys of the input dictionaries."""
    nom_fichier = create_file_and_folder(dossier)
    final_dictionary = {}
    for d in dictionaries:
        final_dictionary.update(d)

    if "time" not in final_dictionary.keys():
        final_dictionary['time'] = datetime.now().strftime("%H:%M:%S")

    if "date" not in final_dictionary.keys():
        final_dictionary['time'] = datetime.now().strftime("%d/%m/%Y")

    fieldnames = update_header(final_dictionary, nom_fichier)
    with open(nom_fichier, 'a', encoding='utf-8') as f:
        writer = csvDictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writerow(final_dictionary)

def readLastCSV(fieldName, nbRows):
    """Reads the last nbRows values of the corresponding column in the data log file and returns a dictionnary with the
    datetime as key and the value requested as value. If the today log file has less than nbRows values, (i.e. if it is
    very early after midnight), then the last data of the previous day will be added."""
    nom_fichier_aujourdhui = date.today().strftime("%Y-%m-%d")
    nom_fichier_aujourdhui = path.join("log", nom_fichier_aujourdhui)
    nb_lines = 0
    with open(nom_fichier_aujourdhui, 'r', encoding='utf-8', newline='') as csvfile:
        nb_lines = len(csvfile.readlines())
    with open(nom_fichier_aujourdhui, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csvDictReader(csvfile, delimiter=";")
        dictionnaire = {}
        i = 0
        for row in reader:
            if i > nb_lines - nbRows:
                dictionnaire[row['time']] = row[fieldName]
            i+=1
        if(len(dictionnaire) < nbRows):
            raise Exception("Dans la fonction readLastCSV. Nombre de données demandées : " + str(nbRows) + " Nombre de données présentes : " + str(len(dictionnaire)))

        return dictionnaire

def readCSV(nomFichier):
    with open(nomFichier, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csvDictReader(csvfile, delimiter=";")
        return [row for row in reader]

def update_header(dictionnaire, nom_fichier):
    """
    Reads the keys of the dictionnary. Adds those keys at the end of the first line if they are not already there
    """
    string_to_add = ""
    with open(nom_fichier, 'r', encoding='utf-8') as f:
        already_present_keys = f.readline().strip().split(delimiter)
        for key in dictionnaire.keys():
            if key not in already_present_keys:
                string_to_add += delimiter + key
                already_present_keys.append(key)
    if string_to_add:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            with open(nom_fichier + "_copy", 'w', encoding='utf-8') as f_out:
                first_line = f.readline().strip()
                other_lines = f.readlines()
                first_line += string_to_add
                f_out.write(first_line + "\n")
                f_out.writelines(other_lines)
        remove(nom_fichier)
        rename(nom_fichier + "_copy", nom_fichier)
    return already_present_keys

def create_file_and_folder(dossier):
    if not path.exists(dossier):
        makedirs(dossier)

    nom_fichier = date.today().strftime("%Y-%m-%d") + ".csv"
    nom_fichier = path.join(dossier, nom_fichier)
    if not path.isfile(nom_fichier):
        with open(nom_fichier, 'a') as f:
            f.write("date" + delimiter + "time")

    return nom_fichier