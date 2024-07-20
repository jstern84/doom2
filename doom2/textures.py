import pyglet

import env
E = env.Env()

def redef_Env(env):
    global E
    E = env

# catégories
AP,PAPIERS,BOIS,GRILLAGES,FENETRES,SOLS,PLAFONDS = 1,2,3,4,5,6,7
IMAGES = {AP:[None,('AP_Asgard_Nuit.jpg',0.2),('AP_Asgard_Jour.jpg',0.2)]
                ,PAPIERS:[None,('bebe.jpg',1)]
                ,BOIS:[None,('mur_bois.tif',1)]
                ,GRILLAGES:[None,('grillage.png',5,False)]
                ,FENETRES:[None,('fenêtre_rouge.png',2,False,True)]
                ,SOLS:[None,('gazon.jpg',1),('carrelage_marbre.tif',1)]
                ,PLAFONDS:[None,('faux_plafond.jpg',1)]}

class Texture():
    def __init__(self, texture, échelle=1,opaque=True,mélange=False):
        self.texture = texture
        self.échelle = échelle
        self.opaque = opaque
        self.mélange = mélange
        self.s1, self.s2, self.t1, self.t2 = 0, 1, 0, 1
    def dupliquer(self): # nécessaire pour les murs coupés en deux
        tex = Texture(self.texture,self.échelle,self.opaque,self.mélange)
        return tex
    def calc_t2s(self,k1,k2):
        s1, s2 = self.s1, self.s2
        if k1!=0: s1 += (self.s2-self.s1)*k1
        if k2!=0: s2 -= (self.s2-self.s1)*(1-k2)
        return (s1,s2)
    def calc_t2t(self,k1,k2):
        t1, t2 = self.t1, self.t2
        if k1!=0: t1 += (self.t2-self.t1)*k1
        if k2!=0: t2 -= (self.t2-self.t1)*(1-k2)
        return (t1,t2)
    def retourner(self):
        self.s1,self.s2 = self.s2,self.s1
        self.t1,self.t2 = self.t2,self.t1
         
class ArrièrePlan():
    def __init__(self, image, fréquence=1, angle0=0):
        self.texture = Texture(image.get_texture())
        self.f = fréquence
        self.largeur, self.hauteur = image.width, image.height
        self.a0 = angle0

class Textures():
    def __init__(self, env=None):
        global E
        self.debug = E.DEBUG
        if env != None: E = env
        self.images = {}
        self.textures = {}
        self.arrières_plans = []
        for cat in IMAGES:
            self.images[cat] = [None]
            for f in IMAGES[cat][1:]:
                try:
                    if len(f)<=2: opaque = True
                    else: opaque = f[2]
                    if len(f)<=3: mélange = False
                    else: mélange = f[3]
                    image = (pyglet.image.load('textures/'+f[0]), f[1], opaque, mélange)
                    self.images[cat].append(image)
                except pyglet.resource.ResourceNotFoundException:
                    if E.DEBUG>E.DEBUG_0: print("# exception (image introuvable) #",end=" ")
    def ret_Texture(self, image, échelle=None, rotation=None):
        cat,no = image[0],image[1]
        image = self.images[cat][no]
        if (cat,no) not in self.textures: # texture pas encore chargée
            texture = image[0].get_texture()
            self.textures[(cat,no)] = texture
        else: texture = self.textures[(cat,no)]
        if échelle == None: échelle = image[1] # échelle par défaut
        t = Texture(texture,échelle,image[2],image[3])
        return t

    def ajout_ArrièrePlan(self, image, échelle=None):
        image = self.images[image[0]][image[1]]
        ap = ArrièrePlan(image[0],image[1])
        self.arrières_plans.append(ap)
        return ap


