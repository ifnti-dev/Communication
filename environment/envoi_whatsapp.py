from whatsappSender import WhatsappSender
import threading
import tkinter as tk
from tkinter import ttk
from contact import Contact


class appli:

    def __init__(self):
        self.ws = None
        self.win = tk.Tk()
        self.win.geometry("1000x270")
        self.label1 = tk.Label(self.win,
                               text="",
                               font=('Helvetica 10'))
        self.boutonLancerWhatsapp = ttk.Button(self.win, text="Lancer Whatsapp web", command=self.lancerWhatsappWeb)
        self.boutonChargerContacts = ttk.Button(self.win, text="Charger contacts", command=self.chargerContacts)
        self.labelNumContacts = tk.Label(self.win, text="0 contacts chargés", font='Helvetica 10')
        self.boutonEnvoyerTout = ttk.Button(self.win, text="Envoyer !", command=self.envoyerTout)
        self.labelEnvoi = tk.Label(self.win, text="", font='Helvetica 10')

        self.textBox = tk.Text(self.win, height=10, width=60)
        scroll = tk.Scrollbar(self.win)
        self.textBox.configure(yscrollcommand=scroll.set)
        # self.textBox.pack(side=tk.LEFT)
        scroll.config(command=self.textBox.yview)
        # scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.boutonTestTemplate = ttk.Button(self.win, text="Tester template", command=self.testerTemplate)
        self.labelTestTemplate = tk.Label(self.win, text="", font='Helvetica 10', wraplength=500, anchor='w')
        insert_text = """Bonjour {prenom} {nom},
Lors de notre passage dans le lycée {lycee} à {ville} en {annee}, tu nous avais indiqué que tu étais intéressé par la formation à l'IFNTI.
Le concours d'entrée aura lieu le lundi 10 juillet 2023.
Inscriptions en ligne : https://forms.gle/9Cvqz7qpobzFgQuN7"""
        self.textBox.insert(tk.END, insert_text)

        self.boutonLancerWhatsapp.grid(row=0, column=0, padx=10, pady=10)
        self.label1.grid(row=0, column=1, padx=10, pady=10)
        self.boutonChargerContacts.grid(row=1, column=0, padx=10, pady=10)
        self.labelNumContacts.grid(row=1, column=1, padx=10, pady=10)
        self.textBox.grid(row=2, column=0, padx=10, pady=10)
        self.boutonTestTemplate.grid(row=2, column=1, padx=10, pady=10)
        self.labelTestTemplate.grid(row=2, column=2, padx=10, pady=10)
        self.boutonEnvoyerTout.grid(row=3, column=0, padx=10, pady=10)
        self.labelEnvoi.grid(row=3, column=1, padx=10, pady=10)

        self.statutEnvoi = "arrêté"
        self.win.mainloop()

    def lancerWhatsappWeb(self):
        self.ws = WhatsappSender('liste_etudiants_interessesSabManaarMurielHegra.csv')

    def chargerContacts(self):
        self.ws.chargerContacts()
        self.labelNumContacts.config(text=str(len(self.ws.contactsAEnvoyer)))

    def envoyerTout(self):
        if self.statutEnvoi == "arrêté":
            self.threadEnvoi = threading.Thread(target=self.ws.envoyerTout, args=(self,))
            self.boutonEnvoyerTout.configure(text="Arrêter l'envoi")
            # self.boutonEnvoyerTout.configure(bg="red")
            self.statutEnvoi = "Envoi en cours"
            self.threadEnvoi.start()
        elif self.statutEnvoi == "Envoi en cours":
            self.boutonEnvoyerTout.configure(text="Arrêt en cours ...")
            self.ws.stopRequired = True
            self.threadEnvoi.join()
            self.boutonEnvoyerTout.configure(text="Envoyer !")
            self.statutEnvoi = "arrêté"

    def testerTemplate(self):
        self.ws.template = self.textBox.get(1.0, "end-1c")
        c = Contact({"id": "325", "ville": "Sokodé", "lycee": "Technique", "nom": "TEOURI", "prenom": "Sabirou",
                     "prefixe_tel": "+228", "num_tel": "90918141", "num_tel2": "", "niveau": "terminale D", "annee":"2022"})
        formatted_string = self.ws.template.format(**c.asDict())
        self.labelTestTemplate.configure(text=formatted_string)


appli()
