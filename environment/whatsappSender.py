from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from Log import logCSV, readCSV, logText
from contact import Contact
from time import sleep

import traceback


class WhatsappSender:

    def __init__(self, nomFichierContacts):
        self.fichier_log = 'log_envoi.csv'
        self.fichier_contacts = nomFichierContacts
        self.piece_jointe = '' # Chemin vers le fichier à joindre. Laisser vide pour ne rien envoyer.
        self.contactsAEnvoyer = []
        self.contactsEnvoyes = []
        self.statut_envoi = ""
        self.template = ""
        self.chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.chrome.get("https://web.whatsapp.com") # objet permettant de manipuler la fenêtre chrome grâce à Sélénium.
        self.stopRequired = False #Cette variable sera passée à True lorsque le programme demandera un arrêt prématuré.

        print("fin du init de whatsapp sender")

    def envoyerTout(self, appli):
        """Fonction qui boucle sur la liste self.contactsAEnvoyer et essaie d'envoyer le message à chaque contact.
        L'attribut "appli" est une référence vers la fenêtre principale afin de pouvoir interagir avec les labels."""
        for i in range(3): # On fait trois passes successives. À chaque fois, la taille de self.contactsAEnvoyer doit diminuer. Si après trois passes, il reste encore des contacts qui ne sont pas envoyés, on considère qu'ils sont tout simplement impossibles.
            for c in self.contactsAEnvoyer[:]:
                for num_tel in {c.num_tel, c.num_tel2}:
                    if self.stopRequired: # Si le programme principal nous demande de nous arrêter tout de suite.
                        return False
                    if num_tel != "":
                        print(num_tel)
                        self.statut_envoi = ""
                        try:
                            self.selectionner_contact(num_tel, c.nom, c.prenom, c.id)
                            message0 = self.template.format(**c.asDict())
                            if self.envoyer_message(num_tel, c.nom, c.prenom, message0, self.piece_jointe, []):
                                self.contactsAEnvoyer.remove(c)
                                self.contactsEnvoyes.append(c)
                                appli.labelEnvoi.configure(text="Envoi réussi à " + c.prenom + " " + c.nom)
                                message = str(len(self.contactsAEnvoyer)) + " contacts restants"
                                appli.labelNumContacts.configure(text=message)
                            else:
                                appli.labelEnvoi.configure(text="Échec de l'envoi à " + c.prenom + " " + c.nom)
                            # On peut éventuellement ici ajouter un nouvel appel à "envoyer_message" avec un autre texte, ou une autre pièce jointe si on veut envoyer plusieurs messages à chaque contacts.
                            print("\n\n\n")
                        except Exception as e:
                            print(str(e))
                        d = c.asDict()
                        d.update({"statut_envoi":self.statut_envoi, "num_tel":num_tel})
                        logCSV(d)
            logText("Fin de la passe n°" + str(i))
        logText("Il reste " + str(len(self.contactsAEnvoyer)) + "contacts qui n'ont pas pu être envoyés malgré les trois passes.")

    def chargerContacts(self):
        """Lit tous les contacts présents dans le fichier csv et les charge dans la liste self.contactsAEnvoyer"""
        reader = readCSV(self.fichier_contacts)
        try:
            self.contactsAEnvoyer = [Contact(c) for c in reader]
        except Exception as e:
            traceback.print_exc()
        return len(self.contactsAEnvoyer)


    def selectionner_contact(self, tel: str, nom: str, prenom: str, num_contact: str, mots_cles_interdits=[]):
        """Recherche, puis sélectionne le contact s'il est trouvé. S'il n'est pas trouvé, renvoie Faux
           Si le contact est trouvé, vérifie qu'aucun des messages passés ne contient un des mot_clés interdits (pour éviter les envois en doublon)
           Au final, ne renvoie vrai que si le contact a été correctement sélectionné et qu'il faut envoyer le message."""
        # On commence par cliquer sur le bouton pour annuler la recherche précédente
        try:
            bouton_annuler_recherche = self.chrome.find_element("xpath", '//button[@aria-label="Annuler la recherche"]')
            bouton_annuler_recherche.click()
            # print("recherche annulée avec succès !")
            sleep(0.5)
        except Exception as e:
            print(str(e))
        # On recherche le champ de saisie de la recherche de contact, pour y taper le numéro de téléphone.
        try:
            search_box = self.chrome.find_element("xpath",
                                             '//div/div/div[@role="textbox"][@contenteditable="true"][@data-testid="chat-list-search"][not(@spellcheck)][@title="Champ de recherche"]')
            search_box.clear()
            search_box.send_keys(tel)
        except Exception as e:
            print(str(e))
        sleep(0.5)
        # Xpath1 ne comporte pas nativement de méthode pour passer en casse majuscule. On fait ça à la main.
        # Maintenant qu'on a tapé le numéro de téléphone dans le champ de recherche, on cherche si un titre de conversation apparaît
        # Si le message "Aucun contact, discussion ou message trouvé" apparaît, cela signifie que cette personne n'a pas whatsapp.
        try:
            titre_UpCass = 'translate(@title,"abcdefghijklmnopqrstuvwxyzèéêëïîäâàüûùöô","ABCDEFGHIJKLMNOPQRSTUVWXYZÈÉÊËÏÎÄÂÀÜÛÙÖÔ")'
            # chaine_chemin_contact = '//div[@aria-label="Résultats de la recherche."]/div[//div[1]/div/span[contains(' + titre_UpCass + ',"{0}") or contains(' + titre_UpCass + ',"{1}")][not(contains(@title, "fait également partie"))]]'
            chaine_chemin_contact = '//div[@aria-label="Résultats de la recherche."]//div[div[@data-testid="cell-frame-title"]/span[contains(' + titre_UpCass + ',"{0}") or contains(' + titre_UpCass + ',"{1}")][not(contains(@title, "fait également"))]]'
            chaine_chemin_contact2 = '//div[@aria-label="Résultats de la recherche."]//div[div/div[@data-testid="cell-frame-title"]/span[contains(' + titre_UpCass + ',"{0}") or contains(' + titre_UpCass + ',"{1}")][not(contains(@title, "fait également"))]]'
            chaine_chemin_contact3 = '//div[@aria-label="Résultats de la recherche."]//div[div/div/div[@data-testid="cell-frame-title"]/span[contains(' + titre_UpCass + ',"{0}") or contains(' + titre_UpCass + ',"{1}")][not(contains(@title, "fait également"))]]'
            chaine_chemin_contact4 = '//div[@aria-label="Résultats de la recherche."]//div[div/div/div/div[@data-testid="cell-frame-title"]/span[contains(' + titre_UpCass + ',"{0}") or contains(' + titre_UpCass + ',"{1}")][not(contains(@title, "fait également"))]]'

            xpath_contact_trouve = chaine_chemin_contact.format(nom.upper(), prenom.upper())
            xpath_contact_trouve2 = chaine_chemin_contact2.format(nom.upper(), prenom.upper())
            xpath_contact_trouve3 = chaine_chemin_contact3.format(nom.upper(), prenom.upper())
            xpath_contact_trouve4 = chaine_chemin_contact4.format(nom.upper(), prenom.upper())
            xpath_contact_non_trouve = '//span[@dir="auto"][@class="i0jNr"][contains(text(),"Aucun contact, discussion ou message trouvé")]'
        except Exception as e:
            print(str(e))
        try:
            index = -1
            (bouton_contact, index) = self.chercher_elements([xpath_contact_trouve, xpath_contact_non_trouve], 3)
            if (index == 1):
                self.statut_envoi += " | Contact officiellement non trouvé"
                print("contact officiellement non trouvé")
                raise Exception("contact officiellement non trouvé")
            elif ((index == -1)):
                self.statut_envoi += "échec de la recherche du contact"
                print("échec de la recherche du contact")
                raise Exception("échec de la recherche du contact")
            try:
                xpath_contact_trouves = [chaine_chemin_contact.format(nom.upper(), prenom.upper()),
                                         chaine_chemin_contact2.format(nom.upper(), prenom.upper()),
                                         chaine_chemin_contact3.format(nom.upper(), prenom.upper()),
                                         chaine_chemin_contact4.format(nom.upper(), prenom.upper())]
                bouton_contacts = [self.chercher_element(xpath_contact_trouve, 1),
                                   self.chercher_element(xpath_contact_trouve2, 1),
                                   self.chercher_element(xpath_contact_trouve3, 1),
                                   self.chercher_element(xpath_contact_trouve4, 1)]

            except Exception as e:
                print("erreur lors de la recherche des boutons alternatifs : " + str(e))
            # Il semble que l'élément cliquable ne soit pas le même d'une conversation à l'autre. Je clique donc sur tout ce que je peux en espérant trouver le bon.
            temps_max = 3
            temps = 0
            trouve = False

            prenom = prenom.upper().replace(" ", "").replace("-", "").replace("'", "")
            nom = nom.upper().replace(" ", "").replace("-", "").replace("'", "")
            while (not (trouve) and (temps < temps_max)):
                print("dans le while recherche de la conversation")
                for num_bouton in range(len(bouton_contacts)):
                    try:
                        print("click sur le bouton " + str(num_bouton) + "   temps = " + str(temps))
                        bouton_contacts[num_bouton].click()
                        sleep(0.5)
                        Titre_conversation = self.chercher_element("//header/div/div/div/span[@dir='auto']", 4).text
                        Titre_conversation = Titre_conversation.upper().replace(" ", "").replace("-", "").replace("'",
                                                                                                                  "")
                        trouve = (prenom in Titre_conversation) or (nom in Titre_conversation) or (
                                str(tel) in Titre_conversation) or (("N" + num_contact) in Titre_conversation)
                        print("Titre_conversation" + Titre_conversation)
                        print("prenom : " + prenom)
                        print("prenom in Titre_conversation : " + str(prenom in Titre_conversation))
                        print("nom : " + nom)
                        print("nom in Titre_conversation : " + str(nom in Titre_conversation))
                        print("tel : " + str(tel))
                        print("str(tel) in Titre_conversation)" + str(str(tel) in Titre_conversation))
                        print("('N' + num_contact) in Titre_conversation : " + str(
                            (("N" + num_contact) in Titre_conversation)))
                        if (trouve):
                            print("Le titre correspond !")
                            break  # On sort de la boucle for et le while va sortir en même temps.
                    except Exception as e:
                        print(str(e))
                temps = temps + 1
            search_box.clear()
            self.statut_envoi += " | contact trouvé 0"

            Titre_conversation = self.chercher_element("//header/div/div/div/span[@dir='auto']", 4).text

            print("Titre conversation : " + Titre_conversation)
            self.statut_envoi += " | 2"
            Titre_conversation = Titre_conversation.upper().replace(" ", "").replace("-", "").replace("'", "")
            self.statut_envoi += " | 2.1"
            if ((prenom in Titre_conversation) or (nom in Titre_conversation) or (tel in Titre_conversation) or (
                    ("N" + num_contact) in Titre_conversation)):
                self.statut_envoi += " | contact sélectionné"
            else:
                print("Mauvais titre")
                self.statut_envoi += " | mais mauvais titre : '" + nom + " " + prenom + "' titre conversation : '" + Titre_conversation + "'"
                print(self.statut_envoi)
                raise Exception(
                    "mauvais titre : '" + nom + " " + prenom + "' titre conversation : '" + Titre_conversation + "'")

        except Exception as e:
            print(str(e))
            self.statut_envoi += " | Contact non trouvé"
            print(self.statut_envoi)
            raise Exception("Contact non trouvé")



    def chercher_contenu_dans_discussion(self, contenu: str):
            """Recherche la chaine passée en argument dans l'historique des message du contact actuellement sélectionné.
               Renvoie vrai si au moins un message contient la chaine, faux sinon."""
            try:
                bouton_chercher = self.chercher_element('//div[@role="button"][@title="Recherche..."]', 2)
                bouton_chercher.click()
            except Exception as e:
                print(e)
            try:
                champ_saisie = self.chercher_element(
                    '//header[//*[contains(text(),"Rechercher des messages")]]/following-sibling::*//div[@contenteditable="true"][@class="_13NKt copyable-text selectable-text"]',
                    3)
                champ_saisie.clear()
                sleep(0.25)
                champ_saisie.send_keys(contenu)
                sleep(0.5)
            except Exception as e:
                self.statut_envoi += " | echec de la sélection de la barre de recherche"
                print(self.statut_envoi)
                raise Exception("echec de la sélection de la barre de recherche : " + str(e))

            chemin_succes = '/html/body/div[1]/div/div/div[2]/div[3]/span/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div[2]/div[1]/span/span/strong[@class="i0jNr"][text()="' + contenu + '"]'
            chemin_succes2 = '//header[//*[contains(text(),"Rechercher des messages")]]/following-sibling::div//div[@class="_3uIPm WYyr1"]/div[@class="_3m_Xw"]/div/div/div/div/div/span[@class="Hy9nV"][contains(@title, "' + contenu + '")]'
            chemin_echec = '//header[//*[contains(text(),"Rechercher des messages")]]/following-sibling::div[@id="pane-side"]/div/div/span[@dir="auto"][@class="i0jNr"][text()="Aucun message trouvé"]'

            index = -1
            (resultat, index) = self.chercher_elements([chemin_succes, chemin_succes2, chemin_echec], 10)
            if (index == 0 or index == 1):
                self.statut_envoi += " | message vraiment trouvé"
                return True
            elif ((index == 2)):
                self.statut_envoi += " | message vraiment non trouvé"
                return False
            else:
                self.statut_envoi += " | valeur index = " + str(index) + "non acceptée dans la recherche de message"
                return True
            champ_saisie.clear()

            # Si rien n'a été renvoyé à ce moment, c'est qu'il y a eu un problème -> Levée d'exception.
            statut_envoi += " | échec de la recherche"
            raise Exception("Échec de la recherche pour le contenu " + contenu)


    def envoyer_message(self, tel: str, nom: str, prenom: str, message: str, image='', mots_cles_interdits=[]):
        """Envoie un message au numéro de téléphone passé en argument, si celui ci est trouvé.
           La chaine de la PJ doit être un chemin absolu vers un fichier présent en local sur l'ordinateur.
           Pour ne pas mettre de PJ, simplement passer une chaine vide, ou bien ne pas préciser cet argument.
           mots_cle_interdits est un tableau de chaines de caractère. S'il n'est pas vide, le message ne sera envoyé que
           si la conversation sélectionnée ne contient aucun des mots clé interdits. (permet d'éviter les messages en doublon, mais prend du temps)"""
        # On commence par chercher si un des mots-clé interdits existe dans la conversation.
        sleep(1)  # On laisse le temps à la conversation de se charger. Sinon, la recherche n'a pas accès aux anciens messages.
        try:
            doit_envoyer = True
            for mot_cle in mots_cles_interdits:
                if (self.chercher_contenu_dans_discussion(mot_cle)):
                    doit_envoyer = False
                    self.statut_envoi += " | le mot-clé interdit '" + mot_cle + "' a été trouvé -> pas d'envoi"
                    return False
            if doit_envoyer:
                self.statut_envoi += " | aucun des mots-clés interdits n'a été trouvé -> envoi"
                print(self.statut_envoi)
        except Exception as e:
            print(str(e))
            self.statut_envoi += " | exception lors de la recherche des mots-clés"
            print(self.statut_envoi)
            raise Exception("exception lors de la recherche des mots-clés")

        # Aucun des mots-clé interdits n'a été trouvé, on continue
        if not self.taper_message(message):
            return False
        sleep(0.5)

        if image == "":
            bouton_envoyer = self.chercher_element("//button[span/@data-testid='send']", 1)
            bouton_envoyer.click()
        else:
            # cliquer sur le bouton joindre
            boutonJoindre = self.chercher_element("//div[@role='button'][@title='Joindre']", 1)
            boutonJoindre.click()

            # sélection du fichier à envoyer
            input_box = self.chrome.find_element(By.tagName('input'))
            input_box.send_keys(image)

            # Attendre que le fichier se charge
            bouton_envoyer = self.chercher_element("//div[@role='button'][span/@data-testid='send']", 35)
            sleep(1)
            bouton_envoyer.click()

        self.statut_envoi += "| envoyé"
        return True

    def chercher_element(self, chemin: str, timeout: int):
        trouve = False
        temps = 0
        while (not trouve):
            try:
                element = self.chrome.find_element("xpath", chemin)
                trouve = True
            except:
                sleep(0.5)
                temps += 0.5
            if (temps > timeout):
                raise Exception("Élément non trouvé pour le chemin : " + chemin)
        return element


    def chercher_elements(self, chemins, timeout: int):
        """Recherche tous les chemins passés en arument et renvoie le premier élément trouvé, ainsi que l'index du chemin auquel il correspond.
           Si rien n'est trouvé avant le timeout, une exception est levée.
           On n'utilise pas la fonction chercher_element afin de faire toutes les recherches en parallèle pour ne pas attendre les timeout à chaque fois."""
        trouve = False
        temps = 0
        element = None
        index = -1
        while (temps < timeout):
            for i in range(len(chemins)):
                try:
                    index = i
                    element = self.chrome.find_element("xpath", chemins[i])
                    trouve = True
                    return (element, index)
                except:
                    sleep(0.3)
                    temps += 0.3
        raise Exception("Élément non trouvé pour les chemins : " + str(chemins))


    def taper_message(self, message: str):
        # taper le message dans le champ message
        # Le caractère '\n' est interprété comme un appui sur la touche "entrer". Ce qui envoie le message. On remplace tous les \n par une combinaison Shift + Enter
        search_box = self.chercher_element('//footer//div[@contenteditable="true"][@spellcheck="true"][@role="textbox"][@title="Taper un message"][@data-testid="conversation-compose-box-input"]', 3)

        for ligne in message.split('\n'):
            search_box.send_keys(ligne)
            ActionChains(self.chrome).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(
                Keys.ENTER).perform()
        return True