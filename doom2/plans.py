import monde as M
import structure as S
import sprites as I
import textures as X

import env
E = env.Env()

def redef_Env(env):
    global E
    E = env
    M.redef_Env(E)
    S.redef_Env(E)

class Plans():
    def __init__(self, struct=None, env=None):
        global E
        if env != None: E=env
        if struct == None: self.S = S.Structure(env)
        else: self.S = struct
        self.r = 1
        self.nb_secteurs = 0
        self.cieux = []

    def ajout_Secteur(self,v,hs,hp,c,sous_secteur=None,portails=None,cs=E.COUL_TEX,cp=E.COUL_TEX,cf=E.COUL_FOND,lumin=0,allumé=0,conn={},ombre=0,no=None,pentes=(0,0),tex={}):
        if no == None:
            no = self.nb_secteurs
            self.nb_secteurs += 1
        s = S.Secteur([(self.r*x,self.r*y) for (x,y) in v], hs, hp, no, c, cs, cp, sous_secteur, portails, cf, lumin, allumé, conn, E.BRILLANCE, ombre, E.SOLEIL, pentes)
        self.S.ss[no] = s
        for m,t in tex.items():
            if s.marche:
                texb = self.S.X.ret_Texture(t)
            else: texb = None
            if type(m)==tuple: # texture répétée + jointures si plusieurs murs
                s.def_TextureJointe(m[0],m[1],self.S.X.ret_Texture(t),texb)
            else: # une texture non répétée
                s.murs[m].def_Texture(self.S.X.ret_Texture(t), texb=texb)

    def def_TexSol(self, secteurs, tex):
        for no in secteurs:
            self.S.ss[no].sol.def_Texture(self.S.X.ret_Texture(tex))
    def def_TexPlafond(self, secteurs, tex):
        for no in secteurs:
            self.S.ss[no].plafond.def_Texture(self.S.X.ret_Texture(tex))

    def ret_Taille(self): # retourne le nombre de secteurs et de murs total
        n = 0
        for s in self.S.ss.values():
            n += len(s.murs)
        return len(self.S.ss),n

    def plan0(self):
        self.r = 50
        self.cieux=[0]
        # textures
        ext = [(0,0),(0,16),(16,16),(16,0)]
        self.ajout_Secteur(ext,0,200,[E.C['blanc']]*4,cs=E.COUL_TEX,cp=E.C['blanc'],no=0,lumin=50,pentes=((0.1,0.1)),tex={(1,4):(X.PAPIERS,1)})
        self.def_TexSol([0],(X.BOIS,1))
        self.def_TexPlafond([0],(X.BOIS,1))
        #self.def_TexPlafond([0],(X.BOIS,1))
        inter = [(6,6),(4,6),(4,4),(6,4)]
        self.ajout_Secteur(inter,0,100,[E.C['rougef']]*4,0,{},cs=E.C['gris'],cp=E.C['grisf'],no=3,lumin=50)
        fen = [(2,4),(2,1),(5,1),(5,4)]
        self.ajout_Secteur(fen,35,0,[E.C['rose']]*4,0,{},cs=E.C['vert'],cp=E.C['rose'],no=1,lumin=50,pentes=((-0.1,0)))
        fen2 = ((3,2),(4,2),(4,3),(3,3))
        self.ajout_Secteur(fen2,5,-10,[E.C['rose']]*4,1,{},cs=E.C['blanc'],cp=E.C['blanc'],no=2,lumin=50)
        fen3 = [(5,6),(5,1),(10,1),(10,6)]
        self.ajout_Secteur(fen3,40,-20,[E.C['rose']]*4,0,{},cs=E.C['blanc'],cp=E.COUL_TEX,no=3,lumin=50,pentes=((0,-0.1)))
        self.def_TexSol([3,1,2],(X.SOLS,1))
        self.def_TexPlafond([3],(X.SOLS,1))
        self.S.I.ajout_Sprite((I.ARBRES,1), (1*self.r,1*self.r,0))
        # arrière plan
        apAsgard = self.S.X.ajout_ArrièrePlan((X.AP,1))
        self.S.def_ArrièrePlan(self.cieux,apAsgard)
        return (8,8,0), (0,0,1),[(0,0)]

    def plan1(self):
        r = self.r
        ext = [(75,120),(75,150),(0,150),(0,230),(180,230),(180,150),(100,150),(100,100),(120,45),(100,45),(100,40),(180,40),(180,0),(0,0),(0,40),(75,40),(75,45),(55,45),(75,100)]
        self.ajout_Secteur(ext,E.H_SOL,E.H_PLAFOND,E.C['vertf'],None,{0:1},E.C['bleu'],E.C['rouge'],E.C['bleuff'],lumin=50)

        cag = [(75,100),(40,100),(40,120),(75,120)]
        self.ajout_Secteur(cag,E.H_SOL-40, E.H_PLAFOND-60, E.C['jauneff'],None,{0:0},E.C['rougeff'],E.C['grisf'],cf=E.C['gris'],lumin=-100,allumé=1)

        pil = [(35,15),(45,15),(45,25),(35,25)]
        self.ajout_Secteur(pil,E.H_SOL,E.H_PLAFOND*2,E.C['vertf'],0)
        pil = [(x+100,y) for (x,y) in pil]
        self.ajout_Secteur(pil,E.H_SOL,E.H_PLAFOND*2,E.C['vertf'],0)

        table = [(40,210),(20,210),(20,180),(40,180)]
        self.ajout_Secteur(table,10,-40,E.C['rose'],0,{},lumin=50)

        marche = [(0,0),(10,0),(10,30),(0,30)]
        self.ajout_Secteur([(x+120,y+200) for (x,y) in marche], 5, -10,E.C['rose'],0,{},lumin=-100,allumé=1,conn=[6,7,8,9,10])
        self.ajout_Secteur([(x+130,y+200) for (x,y) in marche], 10, -10,E.C['rose'],0,{},lumin=-100,allumé=1,conn=[5,7,8,9,10])
        self.ajout_Secteur([(x+140,y+200) for (x,y) in marche], 15, -10,E.C['rose'],0,{},lumin=-100,allumé=1,conn=[6,5,8,9,10])
        self.ajout_Secteur([(x+150,y+200) for (x,y) in marche], 20, -10,E.C['rose'],0,{},lumin=-100,allumé=1,conn=[6,7,5,9,10])
        self.ajout_Secteur([(x+160,y+200) for (x,y) in marche], 25, -10,E.C['rose'],0,{},lumin=-100,allumé=1,conn=[6,7,8,5,10])
        self.ajout_Secteur([(x+170,y+200) for (x,y) in marche], 30, -10,E.C['rose'],0,{},lumin=-100,allumé=1,conn=[6,7,8,9,5])

        fen = [(75,40),(100,40),(100,45),(75,45)]
        self.ajout_Secteur(fen,20,-40,E.C['rose'],0,{})

    def plan3(self):
        self.r = 30
        r = self.r
        self.cieux = [0]
        ext = [(-20,-20),(-20,50),(50,50),(50,-20)]
        self.ajout_Secteur(ext,0,200,[E.C['blanc']]*len(ext),None,{},no=0,lumin=50,conn={20:None})
        # bas
        bas = [(0,0),(0,5),(0,15),(0,19),(6,19),(15,19),(20,19),(20,0)]
        self.ajout_Secteur(bas,0,100,[E.C['vert']]*len(bas),None,{2:32,5:10},cp=E.C['vertf'],no=2,lumin=50)
        corb = [(6,19),(6,29),(29,29),(29,25),(25,25),(15,25),(15,19)]
        self.ajout_Secteur(corb,10,100,[E.C['bleu']]*len(corb),None,{0:2,4:12},cs=E.C['bleuf'],no=10,lumin=50)
        # milieu
        corm = [(29,25),(29,10),(25,10),(25,25)]
        self.ajout_Secteur(corm,0,200,[E.C['gris']]*len(corm),None,{0:10,2:11},cs=E.C['grisf'],no=12,lumin=50,pentes=(100/(15*r),0))  
        # haut
        corh = [(20,10),(25,10),(29,10),(29,6),(20,6)]
        self.ajout_Secteur(corh,100,200,[E.C['jaune']]*len(corh),None,{2:12,0:2},cs=E.C['jaunef'],no=11,lumin=50)  
        haut = [(0,0),(0,19),(20,19),(20,10),(20,6),(20,0),(15,0),(5,0)]
        self.ajout_Secteur(haut,100,200,[E.C['rouge']]*len(haut),None,{4:11,7:0},cs=E.C['jaune'],cp=E.C['rougef'],cf=None,no=1,lumin=50)
        # facade
        fac1 = [(-2,-2),(5,-2),(5,0),(-1,-1),(0,5),(-2,5)]
        self.ajout_Secteur(fac1,0,200,[E.C['blanc']]*len(fac1),0,None,no=21,lumin=50)
        fac2 = [(-2,15),(0,15),(-1,19),(0,20),(5,20),(5,30),(30,30),(30,5),(21,5),(21,-1),(15,0),(15,-2),(22,-2),(22,4),(31,4),(31,31),(4,31),(4,21),(-1,21),(-2,20)]
        self.ajout_Secteur(fac2,0,200,[E.C['blanc']]*len(fac2),0,None,no=22,lumin=50)
        facb = [(5,-2),(15,-2),(15,-1),(5,-1)]
        #self.ajout_Secteur(facb,0,100,[E.C['blanc']]*len(facb),None,{},cs=None,cp=None,no=21,lumin=50)
        # fenêtres
        fenh = [(5,-1),(15,-1),(15,0),(5,0)]
        self.ajout_Secteur(fenh,110,-15,[E.C['blanc']]*len(fenh),0,{1:0,3:1},cs=E.C['rouge'],cp=E.C['rouge'],no=31,lumin=50)
        fenb = [(-1,5),(0,5),(0,15),(-1,15)]
        self.ajout_Secteur(fenb,10,-110,[E.C['blanc']]*len(fenh),0,{2:0,32:2},cs=E.C['rouge'],cp=E.C['rouge'],no=32,lumin=50)
        # table
        table = [(5,5),(10,5),(10,10),(5,10)]
        self.ajout_Secteur(table,15,-30,[E.C['rose']]*4,1,{},no=41)
        self.ajout_Secteur(table,20,0,[E.C['beige']]*4,2,{},no=42,cs=E.C['jaune'],cp=E.C['rose'])
        # étages
        étage_bas0, étage_haut0 = [2,42], [1,41]
        self.S.ajout_Etages(étage_bas0, étage_haut0)
        étage_bas, étage_haut = étage_bas0+[32], étage_haut0+[31]
        self.S.ajout_Exclu(étage_bas, étage_haut)
        self.S.ajout_ExcluOut({10:étage_haut,11:étage_bas,12:étage_bas})
        self.S.ajout_Clip([0],(32,0),E.CLIP_A,étage_haut0)
        self.S.ajout_Clip([0],(31,1),E.CLIP_B,étage_bas0)
        return (-10,-10,0),(20,20,0.3),[(0,0)]


    def plan2(self):
        self.r = 30
        r = self.r
        # cieux
        self.cieux = [0,100]
        H_M = 128 # hauteur maison
        H_E = 128 # hauteur extérieure
        H_S, H_S2 = 5, 60 # hauteur sol maison
        OMB = 0.5
        L_I = 30
        # textures
        tBois = (X.BOIS,1)
        tBébé = (X.PAPIERS,1)
        tGrillage = (X.GRILLAGES,1)
        tGazon = (X.SOLS,1)
        # ciel
        ciel = [(-5.1,-10.1),(-5.1,27.1),(19.1,27.1),(19.1,-10.1)]
        self.ajout_Secteur(ciel,-100,-100,[None]*4,None,None,None,None,no=100)
        # sous secteurs / pièces
        ext = [(-5,-10),(-5,27),(19,27),(19,-10)]
        self.ajout_Secteur(ext,0,H_E,[E.COUL_TEX]*4,None,{},E.COUL_TEX,lumin=L_I,no=0,conn={2:None,3:None,4:None,5:None},ombre=0,tex={(0,4):(tGrillage)})
        maison = list(reversed([(-0.5,-0.5),(-0.5,21.5),(14.5,21.5),(14.5,-0.5)]))
        self.ajout_Secteur(maison,0,H_M-H_E,[E.C['gris']]*4,0,{},no=4,conn={0:None,2:None,3:None,5:None},ombre=OMB)
        pièce1 = [(0,0),(3.8,0),(3.8,6.8),(0,6.8)]
        #self.ajout_Secteur(pièce1,H_S,H_M,[E.C['blanc']]*len(pièce1),None,{},lumin=L_I,no=51,conn={11:[1,2],12:[0],21:[0],33:[0],41:[2],42:[4,5]},ombre=OMB)
        pièce2 = [(0,18.2-2),(5.8,18.2-2),(5.8,21),(0,21)]
        self.ajout_Secteur(pièce2,H_S2,0,[E.C['blanc']]*4,4,{},cp=E.COUL_TEX,lumin=L_I,no=52,conn={14:[1,2],15:[0],24:[0],43:[4,5],46:[3]},ombre=OMB)
        pièce3b = list(reversed([(8.2,14.2),(11,14.2),(14,14.2),(14,14.5),(14,18),(14,19),(11,19),(11,21),(8.2,21)]))
        self.ajout_Secteur(pièce3b,H_S-10,H_S2-2,[E.C['rouge']]*len(pièce3b),None,{5:29,7:1},cp=E.C['rougef'],lumin=L_I,no=53,conn={16:[0],17:[0,3],18:[0],25:[0],29:[0],44:[5,6],45:[1,2],48:[1]},ombre=OMB)
        pièce3h = list(reversed([(8.2,20),(8.2,19),(8.2,14.2),(14,14.2),(14,14.5),(14,18),(14,19),(11,19),(11,20),(11,21),(10,21),(8.5,21),(8.2,21)]))
        self.ajout_Secteur(pièce3h,H_S2,H_M,[E.C['vert']]*len(pièce3h),None,{12:54,4:55,2:25,8:26},cs=E.COUL_TEX,lumin=L_I,no=56,conn={16:[0],17:[0,3],18:[0],25:[0],26:[0],44:[5,6],45:[1,2],48:[1]},ombre=OMB)

        wc = [(11,21),(11,20),(11.2,20),(11.2,19.2),(14,19.2),(14,21)]
        self.ajout_Secteur(wc,H_S2,H_M-H_E,[E.C['blanc']]*6,0,{},lumin=L_I,no=55,conn={17:[1,2],45:[0,4,5]},ombre=OMB)
        jardin = [(-5,27),(-5,21.5),(14,21.5),(14,27)]
        self.ajout_Secteur(jardin,H_S2,0,[E.C['blanc']]*4,0,{},E.COUL_TEX,cp=None,no=3,conn={0:None,2:None,4:None,5:None})
        pente = [(-0.5,0),(-0.5,21.5),(-5,21.5),(-5,0)]
        self.ajout_Secteur(pente,0,0,[E.C['grisf']]*4,0,{},E.COUL_TEX,cp=None,no=2,conn={0:None,3:None,4:None,5:None},pentes=(H_S2/(21.5*r),0))
        allée = [(14.5,-5),(19,-5),(19,27),(14.5,27)]
        self.ajout_Secteur(allée,0,0,[E.C['gris']]*4,0,{},E.COUL_TEX,cp=None,no=5,conn={0:None,2:None,3:None,4:None})
        self.def_TexSol([0,2,3,5],tGazon)
        # murs et cloisons
        cloison1 = [(4,3.5),(3.8,3.5),(3.8,0),(4,0)]
        self.ajout_Secteur(cloison1,0,H_M,[E.C['blanc']]*4,4,None,no=41) # pièce 1
        cloison2 = [(4,4.5),(4,7),(0,7),(0,6.8),(3.8,6.8),(3.8,4.5)]
        self.ajout_Secteur(cloison2,0,H_M,[E.C['blanc']]*6,4,None,no=42) # pièce 1
        cloison3 = [(0,16),(6,16),(6,19),(5.8,19),(5.8,16.2),(0,16.2)]
        self.ajout_Secteur(cloison3,0,H_M,[E.C['blanc']]*6,4,None,no=43,tex={(4,2):tBébé}) # pièce 2
        cloison4 = [(8,19),(8,16),(8,14),(11,14),(11,14.2),(8.2,14.2),(8.2,19)]
        self.ajout_Secteur(cloison4,0,H_M,[E.C['blanc']]*7,4,None,no=44) # pièce 3
        cloison5 = [(11,20),(11,19),(14,19),(14,19.2),(11.2,19.2),(11.2,20)]
        self.ajout_Secteur(cloison5,H_S2,H_M,[E.C['blanc']]*6,4,None,no=45) # wc
        cloison6 = [(6,20),(6,21),(5.8,21),(5.8,20)]
        self.ajout_Secteur(cloison6,0,H_M,[E.C['blanc']]*4,4,None,no=46,tex={(3,1):tBébé}) # pièce 2
        cloison8 = [(8,21),(8,20),(8.2,20),(8.2,21)]
        self.ajout_Secteur(cloison8,H_S2,H_M,[E.C['blanc']]*3+[None],4,None,no=48) # pièce 3


        mur1 = [(4,0),(0,0),(0,1.5),(-0.5,1.5),(-0.5,-0.5),(5.5,-0.5),(5.5,0)] 
        self.ajout_Secteur(mur1,0,H_M,[E.COUL_TEX]*len(mur1),4,None,no=11,tex={(4,2):tBois})
        mur2 = [(0,7),(0,7.5),(-0.5,7.5),(-0.5,4.5),(0,4.5)] 
        self.ajout_Secteur(mur2,0,H_M,[E.COUL_TEX]*len(mur2),4,None,no=12,tex={(3,1):tBois})
        mur3 = [(0,13),(-0.5,13),(-0.5,9),(0,9)] 
        self.ajout_Secteur(mur3,0,H_M,[E.COUL_TEX]*len(mur3),4,None,no=13,tex={(2,1):tBois})
        mur4 = [(0,16.2),(0,21),(1,21),(1,21.5),(-0.5,21.5),(-0.5,14.5),(0,14.5)]
        self.ajout_Secteur(mur4,0,H_M,[E.COUL_TEX]*len(mur4),4,None,no=14,tex={(4,2):tBois,(1,2):tBébé})
        mur5 = [(5.8,21),(6,21),(6,21.5),(4.5,21.5),(4.5,21)] 
        self.ajout_Secteur(mur5,0,H_M,[E.COUL_TEX]*len(mur5),4,None,no=15,tex={(3,1):tBois,(0,1):tBébé})
        mur6 = [(8.5,21),(8.5,21.5),(8,21.5),(8,21)] 
        self.ajout_Secteur(mur6,0,H_M,[E.COUL_TEX]*len(mur6),4,None,no=16,tex={(2,1):tBois})
        mur7 = [(11,21),(14,21),(14,19),(14,18),(14.5,18),(14.5,21.5),(10,21.5),(10,21)] 
        self.ajout_Secteur(mur7,0,H_M,[E.COUL_TEX]*len(mur7),4,None,no=17,tex={(5,2):tBois})
        mur8 = [(14,14),(14,12.5),(14.5,12.5),(14.5,14.5),(14,14.5)] 
        self.ajout_Secteur(mur8,0,H_M,[E.COUL_TEX]*len(mur8),4,None,no=18,tex={(3,1):tBois})
        mur9 = [(14,0),(13.5,0),(13.5,-0.5),(14.5,-0.5),(14.5,7.5),(14,7.5)] 
        self.ajout_Secteur(mur9,0,H_M,[E.COUL_TEX]*len(mur9)*4,4,None,no=19,tex={(3,2):tBois})
        mur10 = [(7,0),(7,-0.5),(8.5,-0.5),(8.5,0)] 
        self.ajout_Secteur(mur10,0,H_M,[E.COUL_TEX]*len(mur10),4,None,no=20,tex={(2,1):tBois})
        #fenêtres et portes
        fen1 = [(0,4.5),(-0.5,4.5),(-0.5,1.5),(0,1.5)]
        self.ajout_Secteur(fen1,20,-15,[E.COUL_TEX]*len(fen1),4,{0:51},E.C['bleuf'],E.C['gris'],no=21,tex={(2,1):tBois})
        fen2 = [(0,9),(-0.5,9),(-0.5,7.5),(0,7.5)]
        self.ajout_Secteur(fen2,15,-15,[E.COUL_TEX]*len(fen2),4,{0:1},E.C['gris'],E.C['gris'],no=22,tex={(2,1):tBois})
        fen3 = [(0,16.5-2),(-0.5,16.5-2),(-0.5,15-2),(0,15-2)]
        self.ajout_Secteur(fen3,15,-15,[E.COUL_TEX]*len(fen3),4,{0:1},E.C['gris'],E.C['gris'],no=23,tex={(2,1):tBois})
        fen4 = [(4.5,21),(4.5,21.5),(1,21.5),(1,21)]
        self.ajout_Secteur(fen4,H_S2+30,-15,[E.COUL_TEX]*len(fen4),4,{},E.C['gris'],E.C['gris'],no=24,tex={(2,1):tBois,(0,1):tBébé})
        fen5 = [(10,21),(10,21.5),(8.5,21.5),(8.5,21)]
        self.ajout_Secteur(fen5,H_S2+20,-15,[E.COUL_TEX]*len(fen5),4,{},E.C['gris'],E.C['gris'],no=25,tex={(2,1):tBois})
        fen6 = [(14,14.5),(14.5,14.5),(14.5,18),(14,18)]
        self.ajout_Secteur(fen6,H_S2+10,-15,[E.COUL_TEX]*len(fen6),4,{},E.C['gris'],E.C['gris'],no=26,tex={(2,1):tBois})
        fen7 = [(14,7.5),(14.5,7.5),(14.5,12.5),(14,12.5)]
        self.ajout_Secteur(fen7,15,-15,[E.COUL_TEX]*len(fen7),4,{0:1},E.C['gris'],E.C['gris'],no=27,tex={(2,1):tBois})
        fen8 = [(8.5,0),(8.5,-0.5),(13.5,-0.5),(13.5,0)]
        self.ajout_Secteur(fen8,65,-15,[E.COUL_TEX]*len(fen8),4,{0:1},E.C['gris'],E.C['gris'],no=28,tex={(2,1):tBois})
        fen9 = [(14,14.5),(14.5,14.5),(14.5,18),(14,18)]
        self.ajout_Secteur(fen9,H_S+10,H_S2-H_M-10,[E.COUL_TEX]*len(fen9),4,{0:53,2:0},E.C['gris'],None,no=29,tex={(2,1):tBois})
        porte1 = [(5.5,0),(5.5,-0.5),(7,-0.5),(7,0)]
        self.ajout_Secteur(porte1,2.5,-30,[E.COUL_TEX]*len(porte1),4,{2:0},E.C['bleuf'],E.C['gris'],no=31,tex={(2,1):tBois}) # entrée bas
        porte2 = [(8,21),(8,21.5),(6,21.5),(6,21)]
        self.ajout_Secteur(porte2,H_S2+2.5,-5,[E.COUL_TEX]*len(porte2),4,{},E.C['rougef'],E.C['gris'],no=32,tex={(2,1):tBois}) # sortie haute
        porte3 = [(3.8,3.5),(4,3.5),(4,4.5),(3.8,4.5)]
        self.ajout_Secteur(porte3,H_S,-60,[E.C['blanc']]*4,4,{},E.C['gris'],E.C['gris'],no=33) # pièce 1
        porte4 = [(11,14),(14,14),(14,14.2),(11,14.2)]
        self.ajout_Secteur(porte4,H_S,H_S2-H_M-2,[E.C['blanc']]*4,4,{},no=34)

        # inter
        conn_inter = {11:[0],12:[1],13:[0],14:[0],18:[1],19:[0,1],20:[0],22:[0],23:[0],27:[0],28:[0],31:[0],33:[2],41:[0,1],42:[0,1,2],43:[1],44:[2,3]}
        inter = [(4,7),(4,0),(14,0),(14,14),(6,14),(6,16),(0,16),(0,7)]
        # palier
        conn_palier = {32:[0],43:[2,3],44:[0,1],46:[0,1],48:[0,3]}
        palier = [(6,21),(6,20),(5.8,20),(5.8,19),(6,19),(6,18.5),(8,18.5),(8,19),(8.2,19),(8.2,20),(8,20),(8,21)]
        # marches
        l, h = 0.5, 6
        marche = [(8,14),(8,14+l),(6,14+l),(6,14)]
        for i in range(1,10):
            if i>4:
                conn = {}#60+j:None for j in range(5,10) if i!=j}
                #conn[54] = None
                self.ajout_Secteur(marche,H_S+i*h,-60+i*h,[E.C['blanc']]*4,4,{},E.C['rose'],lumin=L_I,no=60+i,conn=conn,ombre=OMB,pentes=(0,h/(l*r)))
                conn_palier[60+i] = None
            else:
                conn = {}#60+j:None for j in range(1,5) if i!=j}
                #conn[1] = None
                self.ajout_Secteur(marche,H_S+i*h,-34,[E.C['blanc']]*4,4,{},E.C['rose'],lumin=L_I,no=60+i,conn=conn,ombre=OMB)
                conn_inter[60+i] = None
            marche = [(x,y+l) for (x,y) in marche]
        # inter et palier
        #self.ajout_Secteur(inter,H_S,H_M-H_E,[E.C['blanc']]*len(inter),4,{},E.C['bleuf'],lumin=L_I,no=1,conn=conn_inter,ombre=OMB) 
        self.ajout_Secteur(palier,H_S2,0,[E.C['blanc']]*len(palier),4,{},E.C['blanc'],lumin=L_I,no=54,conn=conn_palier,ombre=OMB)
        # étages
        étage_bas0, étage_haut0 = [53,29], [56,26]
        self.S.ajout_Etages([53,29],[56,26])
        #self.S.def_Etages([26,29])
        étage_bas, étage_haut = étage_bas0+[34], étage_haut0
        self.S.ajout_Exclu(étage_bas, étage_haut) 
        self.S.ajout_ExcluEtage(étage_haut, [27,0,2,4,33,31,51,28,22])
        self.S.ajout_ExcluEtage(étage_bas, [54,52,32,24,3])
        self.S.ajout_Clip([5],(34,1),E.CLIP_A,étage_haut0)
        self.S.ajout_Clip([5,3],(26,2),E.CLIP_N,étage_bas0)
        self.S.ajout_Clip([5,3],(29,2),E.CLIP_S,étage_haut0)
        # sprites
        self.S.I.ajout_Sprite((I.ARBRES,1), (1*r,23*r,H_S2))
        self.S.I.ajout_Sprite((I.VOITURES,1), (2*r,-4*r,H_S))
        self.S.I.ajout_Sprite((I.POUBELLES,1), (16*r,-4.5*r,H_S))
        self.S.I.ajout_Sprite((I.POUBELLES,2), (18*r,-4.5*r,H_S))
        # jointures
        self.S.ajout_Jointures([(43,5),(14,1,2),(24,0),(15,0),(46,3)]) # pièce 2 bébé
        self.S.ajout_Jointures([(11,5),(31,2),(20,2),(28,2),(19,3,4),(27,2),(18,3),(29,2),(17,5,6),(25,2),(16,2),(32,2),(15,3),(24,2),(14,4,5),(23,2),(13,2),(22,2),(12,3),(21,2),(11,4)]) # extérieur bois
        apAsgard = self.S.X.ajout_ArrièrePlan((X.AP,2))
        self.S.def_ArrièrePlan(self.cieux,apAsgard)
        self.S.def_Vitrage((28,2),self.S.X.ret_Texture((X.FENETRES,1)))
        self.def_TexPlafond([4,52,56],(X.PLAFONDS,1))
        self.def_TexSol([4],(X.SOLS,2))

        return (-3,-3,0),(6,6,0.5),[(44,1),(43,1)]