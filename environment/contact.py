class Contact:

    def __init__(self, dictionnaire):
        self.id = dictionnaire["id"]
        self.ville = dictionnaire["ville"]
        self.lycee = dictionnaire["lycee"]
        self.nom = dictionnaire["nom"]
        self.prenom = dictionnaire["prenom"]
        self.prefixe_tel = dictionnaire["prefixe_tel"]
        self.num_tel = dictionnaire["num_tel"]
        self.num_tel2 = dictionnaire["num_tel2"]
        self.annee = dictionnaire["annee"]
        self.niveau = dictionnaire["niveau"]

    def asDict(self):
        return {"id":self.id,
                "ville":self.ville,
                "lycee":self.lycee,
                "nom":self.nom,
                "prenom":self.prenom,
                "prefixe_tel":self.prefixe_tel,
                "annee":self.annee}