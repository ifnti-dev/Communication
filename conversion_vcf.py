def ajouter_numero(numero, ligne_actuelle, liste_numeros, message_err):
    if(liste_numeros.count(numero) == 0):
        liste_numeros.append(numero)
    else:
        return "\n\n" + \
               "   / \    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" + \
               "  / | \          erreur : numéro " + str(numero) + " en doublon\n" + \
               " /  .  \         lignes " + str(liste_numeros.index(numero)-2) + " et " + str(ligne_actuelle) + "\n" + \
               " -------  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    return ""

with open("liste_etudiants_interesses.csv", "r") as filin:
    with open("contacts.vcf", "w") as filout:
        liste_nums = []
        message_erreur = "\n"
        nbr_lignes = 0
        for ligne in filin:

            nbr_lignes = nbr_lignes + 1
            ligne = ligne.split(",")
            num_contact = ligne[0].replace("\n", "")
            nom = ligne[3].replace("\n", "")
            prenom = ligne[4].replace("\n", "")
            prefixe = ligne[5]
            num_tel = ligne[6].replace("-", "").replace("\n", "")
            num_tel_2 = ligne[7].replace("-", "").replace("\n", "")
            annee = ligne[9].replace("\n", "")
            
            #print("n° ligne : " + str(nbr_lignes) + " | num_tel : " +  num_tel + " | num_tel_2 : " + num_tel_2 + " | liste_nums : " + liste_nums)
            
            a_afficher = "{0:<20s}{1:<20s}{2:<10s}{3:<10s}".format(nom, prenom, num_tel, num_tel_2)
            #print(a_afficher)
            
            message_erreur += ajouter_numero(num_tel, nbr_lignes, liste_nums, message_erreur)
            
            if(num_tel_2 != ""):
                message_erreur += ajouter_numero(num_tel_2, nbr_lignes, liste_nums, message_erreur)
                num_tel_2 = "TEL;CELL:+228" + num_tel_2 + "\n"
                           # "TEL;CELL:" + num_tel_2 + "\n" + \
            if(message_erreur != "\n"):
                break
                
            string = "BEGIN:VCARD\n" + \
                     "VERSION:2.1\n" + \
                     "N:" + nom + ";" + prenom + ";;;" + annee + " N" + num_contact + "\n" + \
                     "FN:" + prenom + " " + nom + "\n" + \
                     "TEL;CELL:" + prefixe + num_tel + "\n" + \
                     num_tel_2 + \
                     "END:VCARD\n"
                     
                     #"N:" + nom + ";" + prenom + ";;;\n" + \
                     #"FN:" + prenom + " " + nom + "\n" + \
            filout.write(string)
            
print("\n" + str(nbr_lignes) + " contacts convertis, pour un total de " + str(len(liste_nums)) + " numéros")
print(message_erreur)





    
