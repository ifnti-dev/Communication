from whatsappSender import WhatsappSender
import threading
from tkinter import *
from tkinter import ttk
class appli:

    def __init__(self):
        self.ws = None
        self.win = Tk()
        self.win.geometry("1000x270")
        self.label1 = Label(self.win,text="Commencer par ouvrir Whatsapp web en cliquant sur le bouton ci-dessous, puis vous y connecter.", font=('Helvetica 10'))
        #self.label1.pack(pady=20)
        self.boutonLancerWhatsapp = ttk.Button(self.win, text="Lancer Whatsapp web", command=self.lancerWhatsappWeb)
        #self.boutonLancerWhatsapp.pack()
        self.boutonChargerContacts = ttk.Button(self.win, text="Charger contacts", command=self.chargerContacts)
        self.labelNumContacts = Label(self.win, text="0 contacts chargés", font='Helvetica 10')
        #self.boutonChargerContacts.pack()
        self.boutonEnvoyerTout = ttk.Button(self.win, text="Envoyer !", command=self.envoyerTout)
        self.labelEnvoi = Label(self.win, text="", font='Helvetica 10')
        #self.boutonEnvoyerTout.pack()

        self.boutonLancerWhatsapp.grid(row=0, column=0, padx=10, pady=10)
        self.label1.grid(row=0, column=1, padx=10, pady=10)
        self.boutonChargerContacts.grid(row=1, column=0, padx=10, pady=10)
        self.labelNumContacts.grid(row=1, column=1, padx=10, pady=10)
        self.boutonEnvoyerTout.grid(row=2, column=0, padx=10, pady=10)
        self.labelEnvoi.grid(row=2, column=1, padx=10, pady=10)

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
            #self.boutonEnvoyerTout.configure(bg="red")
            self.statutEnvoi = "Envoi en cours"
            self.threadEnvoi.start()
        elif self.statutEnvoi == "Envoi en cours":
            self.ws.stopRequired = True
            self.boutonEnvoyerTout.configure(text="Arrêt en cours ...")
            self.threadEnvoi.join()
            self.boutonEnvoyerTout.configure(text="Envoyer !")
            self.statutEnvoi = "arrêté"
        # self.ws.envoyerTout()
        # TODO faire en sorte que la suite soit dans un thread à part avec un bouton "arrêter l'envoi".
        #  Comme ça, on peut couper l'envoi en cours de route sans pour autant devoir se reconnecter à Whatsapp Web.


appli()


