import pyglet
from pyglet import gl

from copy import deepcopy
from math import sqrt,cos, sin, tan, floor, ceil

import monde
import structure as C
import tracer as T
import zbuffer as Z

import env
E = env.Env()

def redef_Env(env):
    global E
    E = env
    C.redef_Env(E)
    T.redef_Env(E)

class recalc_3D(env.Exceptions):
    pass

class Scène3D():
    def __init__(self, monde, env=None):
        global E
        self.debug = E.DEBUG
        self.M = monde
        if env != None:
            E = env
            T.redef_Env(E)
        self.nb = [0,0,0,0,0,0,0]
        self.zBuf = Z.zBuffer(E.X_RES, E.Y_RES)
        self.lots3D = []
        self.murs3D=None


    def calc_Scène3D(self, bsp=None):
        if bsp == None:
            # self.j.entrée_ss = False # devenu inutile avec j.arrêt()
            self.zBuf.mà0()
            self.nb = [0,0,0,0,0,0]
            mur = self.M.bsp
            #self.tracés3D = []
            self.sols3D = []
            for m in self.M.murs_retournés:
                m.retourner()
            self.M.murs_retournés = []
            # calcul de la hauteur du joueur
            h_sol = self.M.calc_HauteurPied()
            if h_sol!=self.M.j.h_sol:
                self.M.j.h_decal = self.M.j.h_sol - h_sol
            self.M.j.h_sol = h_sol
            self.T = T.Tracer(self.M.S.X.textures) # initialisation du tracer
        elif (type(bsp) == list) and (bsp != []): # on est arrivés au sprites-feuilles
        
        # ******************* GESTION SPRITES *********************

            t = T.Tracé_Sprites()
            for s in bsp: # on parcourt les sprites
                visible = s.init_SiVisible(self.M)
                if visible and E.SPRITEX_ZBUFFER:
                    x1, x2 = max(0,s.X), min(E.X_RES,s.X+s.largeur)
                    if not self.zBuf.xBuf.màj(x1,x2,True): visible = False # passage dans le X zBuffer
                if visible and E.SPRITEY_ZBUFFER:
                    ys, yp = max(0,s.Y), min(E.Y_RES,s.Y+s.hauteur)
                    bas, haut = self.zBuf.yBuf.màj(x1,x2,ys,yp,ys,yp,False) # Y zBuffer
                    if (not bas[1]) or (not haut[0]): visible = False
                if visible:
                    t.ajout_Sprite(s)
            if (t.sprites != []): self.T.tracés.append(t)
            return
        else:
            mur = bsp
        hj = self.M.j.hauteur()
        self.nb[0] += 1
        m = mur.n
        if m.sous_secteur: sp = self.M.secteurs[m.s.ss] # secteur parent si sous_secteur
        # à exclure ?
        if (m.s.no in self.M.S.exclu) and (self.M.j.s in self.M.S.exclu[m.s.no]):
            exclu = True
        else: exclu = False
        # vecteurs JA et JB pour déterminer de quel côté
        v1 = [m.x1-self.M.j.x, m.y1-self.M.j.y]
        v2 = [m.x2-self.M.j.x, m.y2-self.M.j.y]
        PV, PV2 = m.calc_PV(v1), m.calc_PV(v2)
        if abs(PV2)>abs(PV): PV = PV2
        a_droite = (PV > 0)
                
        # portail à retourner ?
        if (PV < 0) and m.portail: # pas PV=0 pour éviter la division par 0
            self.M.murs_retournés.append(mur)
            mur.retourner()
            PV = -PV
            v1, v2 = v2, v1

        # ******************* GESTION COLLISIONS *********************

        # proche d'un mur retourné : collision ? franchissement de portail ?
        if self.M.j.deplacement and (abs(PV) < E.D_COLLISION):# and (not a_droite) :
            self.nb[5] += 1
            a_droite_p = m.a_droite(self.M.j.xp,self.M.j.yp)
            if self.debug>=E.DEBUG_1: print("franchissement portail ??",m.s.no,((self.M.j.xp,self.M.j.yp),(self.M.j.yp,self.M.j.y)),m.retourné)
            if (a_droite_p != a_droite): # franchissement de la ligne ?
                franchissement = self.M.j.franchissement(m)
                if self.debug>=E.DEBUG_1: print("franchissement portail ?",m.s.no)
                if franchissement: # fanchissement du segment ?
                    S_joueur = self.M.ret_SecteursParents(self.M.secteurs[self.M.j.s]) # secteur parent courant
                    S_mur = self.M.ret_SecteursParents(m.s)
                    if (not exclu) and E.COLLISION and (S_joueur[0].no==S_mur[0].no) and (m.normal or m.pilier): # collision ?
                        self.M.j.glisser(m.u)
                        raise recalc_3D

                    # franchissement de portail : changement de secteur
                    if (not exclu) and m.portail:
                        if self.debug>=E.DEBUG_1: print("franchissement portail:",m.s.no)
                        if m.marche:
                            if not m.retourné:
                                # sorti d'un sous-secteur et non déjà entré dans un autre sous-secteur => secteur
                                if (self.M.j.s==m.s.no):
                                    s = sp
                                    self.M.j.s = s.no
                                    if self.debug>=E.DEBUG_1: print("entrée secteur:",s.no)
                            else: # entrée dans un sous-secteur
                                if m.s.no not in S_joueur: # on garde le secteur le moins parent
                                    s = self.M.secteurs[m.s.no]
                                    self.M.j.s = m.s.no
                                    if self.debug>=E.DEBUG_1: print("entrée sous-secteur:",m.s.no)
                        elif not m.retourné: # portail retourné => vrai portail
                            s = self.M.secteurs[m.s.no]
                            self.M.j.s = m.s.no
                            if self.debug>=E.DEBUG_1: print("entrée secteur (par portail):",m.s.no)
                            self.M.j.aller() # va avec le raise suivant sinon on boucle
                            raise recalc_3D

        if m.retourné: a_droite = True

        # ******************* GESTION FILTRAGE VISIBILITE *********************

        # TEST 1 : est-on du bon côté de la ligne du mur ?
        if a_droite:
            if mur.d != None: self.calc_Scène3D(mur.d) # algo du "peintre" inversé : on va d'abord au plus près
            self.nb[1] += 1
            # TEST 2 : faut-il zapper un demi-plan ? (direction de la ligne du mur hors champ)
            Ng, Nd = m.calc_PS(self.M.j.ug), m.calc_PS(self.M.j.ud)
            if (not exclu) and (Ng < 0 or Nd < 0):
                self.nb[2] += 1
                # par défaut mur visible
                visible = True
                # coordonnées référentiel joueur
                X1, X2 = self.M.j.calc_PS(v1), self.M.j.calc_PS(v2)
                Y1, Y2 = self.M.j.calc_PV(v1), self.M.j.calc_PV(v2)
                try:
                    ta1 = Y1/X1
                except:
                    if E.DEBUG>E.DEBUG_0: print("# exception (division par X1 nul) #",end=" ")
                    if Y1>0: ta1 = E.TAN_DA_VISION # de toute manière on coupera à gauche
                    else: ta1 = -E.TAN_DA_VISION
                try:
                    ta2 = Y2/X2
                except:
                    if E.DEBUG>E.DEBUG_0: print("# exception (division par X2 nul) #",end=" ")
                    if Y2>0: ta2 = E.TAN_DA_VISION # de toute manière on coupera à droite
                    else: ta2 = -E.TAN_DA_VISION
                # TEST 3 : mur à côté du champ de vision ?
                if (X1<=0 and X2<=0) or (Y1<=0 and ((X1<=0 and (Ng>=0 or Nd<0)) or (X1>=0 and ta1<=-E.TAN_DA_VISION))) or ((Y2>=0 and (Nd>=0 or Ng<=0)) and (X2<=0 or (X2>=0 and ta2>=E.TAN_DA_VISION))):
                    visible = False
                if visible:
                    self.nb[3] += 1
                    coupé_D, coupé_G = False, False
                    sk1,sk2 = 0,1
                    # s'il faut couper:
                    if Nd<0 and ((X2>=0 and ta2<=-E.TAN_DA_VISION) or (X2<=0 and ta2>=-E.TAN_DA_VISION)) : # on coupe sur ud
                        coupé_D = True
                        ta2 = -E.TAN_DA_VISION
                    if Ng<0 and ((X1>=0 and ta1>=E.TAN_DA_VISION) or (X1<=0 and ta1<=E.TAN_DA_VISION)): # on coupe sur ug
                        coupé_G = True
                        ta1 = E.TAN_DA_VISION
                    # hauteurs sol et plafond
                    if m.marche:
                        hs = self.M.calc_HauteurSol(sp)# calcul récursif de sous-secteurs [self.M.secteurs[m.s.ss].h_sol]
                        hp = hs+m.s.h_sol
                        hp2 = self.M.calc_HauteurPlafond(sp)# calcul récursif de sous-secteurs [self.M.secteurs[m.s.ss].h_plafond]
                        hs2 = hp2+m.s.h_plafond
                    else:
                        hs = m.s.h_sol
                        hp = m.s.h_plafond

                    # ******************* GESTION PROJECTION *********************

                    # on projette
                    X1_p, Y1_p = X1, Y1
                    if coupé_G:
                        x1 = -E.DX_RES
                        d1 = -PV/Ng
                        X1, Y1 = d1*E.COS_DA_VISION, d1*E.SIN_DA_VISION
                        # coordonnées texture
                        if (self.M.S.a_Texture(m)):
                            if X1_p != X2:
                                sk1 = round((X1-X1_p)/(X2-X1_p),E.NB_DECIMALES)
                            else:
                                sk1 = round((Y1-Y1_p)/(Y2-Y1_p),E.NB_DECIMALES)
                        DS, DP, Ds, Dp = 0, 0, 0, 0 # dénivelés
                        if m.s.sol.incliné or m.s.plafond.incliné or (m.marche and (sp.sol.incliné or sp.plafond.incliné)):
                            x, y = self.M.j.x+d1*self.M.j.ug[0], self.M.j.y+d1*self.M.j.ug[1]
                            if m.s.sol.incliné: Ds = m.s.sol.calc_Dénivelé((x,y))
                            if m.s.plafond.incliné: Dp = m.s.plafond.calc_Dénivelé((x,y))
                            if m.marche:
                                if sp.sol.incliné: DS = sp.sol.calc_Dénivelé((x,y))
                                if sp.plafond.incliné: DP = sp.plafond.calc_Dénivelé((x,y))
                        k1 = E.Rc/d1
                        if m.marche:
                            ys1, yp1 = (DS+hs-hj)*k1, (Ds+hp-hj)*k1
                            ys1b, yp1b = (Dp+hs2-hj)*k1, (DP+hp2-hj)*k1
                        else:
                            ys1, yp1 = (Ds+hs-hj)*k1, (Dp+hp-hj)*k1
                    else:
                        x1 = -E.R0*ta1
                        k1 = E.R0/X1
                        if m.marche:
                            DS, DP = 0, 0
                            if sp.sol.incliné: DS = sp.sol.calc_Dénivelé((m.x1,m.y1))
                            if sp.plafond.incliné: DP = sp.plafond.calc_Dénivelé((m.x1,m.y1))
                            ys1, yp1 = (DS+hs-hj)*k1, (m.hs1+hp-hj)*k1
                            ys1b, yp1b = (m.hp1+hs2-hj)*k1, (DP+hp2-hj)*k1
                        else:
                            ys1, yp1 = (m.hs1+hs-hj)*k1, (m.hp1+hp-hj)*k1
                    if coupé_D:
                        x2 = E.DX_RES
                        d2 = -PV/Nd
                        X2_p, X2 = X2, d2*E.COS_DA_VISION
                        Y2_p, Y2 = Y2, -d2*E.SIN_DA_VISION
                        # coordonnées texture
                        if (self.M.S.a_Texture(m)):
                            if X1_p != X2_p:
                                sk2 = (X2-X1_p)/(X2_p-X1_p)
                            else:
                                sk2 = (Y2-Y1_p)/(Y2_p-Y1_p)
                        DS, DP, Ds, Dp = 0, 0, 0, 0 # dénivelés (secteur parent, ys/yp)
                        if m.s.sol.incliné or m.s.plafond.incliné or (m.marche and (sp.sol.incliné or sp.plafond.incliné)):
                            x, y = self.M.j.x+d2*self.M.j.ud[0], self.M.j.y+d2*self.M.j.ud[1]
                            if m.s.sol.incliné: Ds = m.s.sol.calc_Dénivelé((x,y))
                            if m.s.plafond.incliné: Dp = m.s.plafond.calc_Dénivelé((x,y))
                            if m.marche:
                                if sp.sol.incliné: DS = sp.sol.calc_Dénivelé((x,y))
                                if sp.plafond.incliné: DP = sp.plafond.calc_Dénivelé((x,y))
                        k2 = E.Rc/d2
                        if m.marche:
                            ys2, yp2 = (DS+hs-hj)*k2, (Ds+hp-hj)*k2
                            ys2b, yp2b = (Dp+hs2-hj)*k2, (DP+hp2-hj)*k2
                        else:
                            ys2, yp2 = (Ds+hs-hj)*k2, (Dp+hp-hj)*k2
                    else:
                        x2 = -E.R0*ta2
                        k2 = E.R0/X2
                        ys2, yp2 = (m.hs2+hs-hj)*k2, (m.hp2+hp-hj)*k2
                        if m.marche:
                            DS, DP = 0, 0
                            if sp.sol.incliné: DS = sp.sol.calc_Dénivelé((m.x2,m.y2))
                            if sp.plafond.incliné: DP = sp.plafond.calc_Dénivelé((m.x2,m.y2))
                            ys2, yp2 = (DS+hs-hj)*k2, (m.hs2+hp-hj)*k2
                            ys2b, yp2b = (m.hp2+hs2-hj)*k2, (DP+hp2-hj)*k2
                        else:
                            ys2, yp2 = (m.hs2+hs-hj)*k2, (m.hp2+hp-hj)*k2
                    x1, ys1, yp1 = x1+E.DX_RES, (ys1+E.DY_RES), (yp1+E.DY_RES)
                    x2, ys2, yp2 = x2+E.DX_RES, (ys2+E.DY_RES), (yp2+E.DY_RES)
                    if m.marche:
                        ys1b, yp1b = round((ys1b+E.DY_RES),E.NB_DECIMALES), round((yp1b+E.DY_RES),E.NB_DECIMALES)
                        ys2b, yp2b = round((ys2b+E.DY_RES),E.NB_DECIMALES), round((yp2b+E.DY_RES),E.NB_DECIMALES)
                    x1,ys1,yp1 = round(x1,E.NB_DECIMALES),round(ys1,E.NB_DECIMALES),round(yp1,E.NB_DECIMALES)
                    x2,ys2,yp2 = round(x2,E.NB_DECIMALES),round(ys2,E.NB_DECIMALES),round(yp2,E.NB_DECIMALES)

                    # ******************* GESTION QUADS A TRACER *********************

                    # TEST 4 : totalement caché (X-zBuffer) ?
                    if (not E.X_ZBUFFER) or self.zBuf.xBuf.màj(x1,x2,m.portail or bool(m.s.étage) or not m.est_Opaque()): # 3 cas de non màj : portail/étage/pas de couleur/transparent
                        self.nb[4] += 1
                        # catégories à tracer ...
                        # ... murs (bas et haut)
                        yaMur = (m.normal or m.pilier or (m.marche and not m.retourné)) and (ys1!=yp1 or ys2!=yp2) and (m.c!=None)
                        yaMurHaut = m.marche and (not m.retourné) and (ys1b!=yp1b or ys2b!=yp2b)
                        yaVitrage = m.marche and m.vitrage and (m.texc!=None) # on vérifie tout au cas où
                        # ... sol (bas) et plafond (haut)
                        yaSol = (m.s.sol.c!=None) # pour sol incolore à h=0 de sous_secteur par exemple
                        yaPlafond = (m.s.plafond.c!=None or m.s.ciel) # pour plafond incolore à -0 de sous_secteur par exemple
                        # TEST 5 : caché (Y-zBuffer) ? => quoi tracer ?
                        if m.marche:
                            # CLIPPING (pour étages)
                            if (self.M.j.s,m.s.no) in self.M.S.clips: # secteurs vu_depuis et vu_àtravers ok
                                if self.debug>=E.DEBUG_2: print("clip ?",self.M.j.s,m.s.no,end="_")
                                clip = self.M.S.clips[(self.M.j.s,m.s.no)] 
                                if (m.no == clip.mur) and (not m.retourné): # mur pour clipping ok
                                    if clip.côté == E.CLIP_A:
                                        if coupé_D: self.T.x_clipA = E.X_RES
                                        else: self.T.x_clipA = x2
                                        self.T.clippésA = clip.secteurs
                                        if self.debug>=E.DEBUG_2: print("A:",m.s.no,m.no,x2,clip.secteurs)
                                    elif clip.côté == E.CLIP_B:
                                        if coupé_G: self.T.x_clipB = 0
                                        else: self.T.x_clipB = x1
                                        self.T.clippésB = clip.secteurs
                                        if self.debug>=E.DEBUG_2: print("B:",m.s.no,m.no,x1,clip.secteurs)
                                    elif clip.côté == E.CLIP_S:
                                        N = [ys2b-ys1b,x1-x2] # vecteur normal à la ligne de clip
                                        l = 1 #sqrt(N[0]**2+N[1]**2) [normalisation inutile]
                                        N[0], N[1] = N[0]/l, N[1]/l
                                        d = -(N[0]*x1+N[1]*ys1b) # produit scalaire
                                        self.T.planS = N[0],N[1],d
                                        self.T.clippésS = clip.secteurs
                                        if self.debug>=E.DEBUG_2: print("S:",m.s.no,m.no,N,d,"_",x1,ys1b,clip.secteurs)
                                    elif clip.côté == E.CLIP_N:
                                        N = [yp2-yp1,x1-x2] # vecteur normal à la ligne de clip
                                        l = 1#sqrt(N[0]**2+N[1]**2) [normalisation inutile]
                                        N[0], N[1] = N[0]/l, N[1]/l
                                        d = -(N[0]*x1+N[1]*yp1) # produit scalaire
                                        self.T.planN = N[0],N[1],d
                                        self.T.clippésN = clip.secteurs
                                        if self.debug>=E.DEBUG_2: print("N:",m.s.no,m.no,N,d,"_",x1,yp1,clip.secteurs)
                            if E.Y_ZBUFFER:
                                bas, haut = self.zBuf.yBuf.màj(x1,x2,min(yp1,yp2),max(ys1b,ys2b),max(yp1,yp2),min(ys1b,ys2b), not m.s.étage and m.est_Opaque()) # 2 cas de non màj : étage/pas de couleur
                            else: bas, haut = (True,True),(True,True)
                            if not bas[0]: # mur bas et sol cachés par la fenêtre
                                yaMur, yaSol = False, False
                            if not haut[1] : # mur haut et plafond cachés par la fenêtre
                                yaMurHaut, yaPlafond = False, False
                            if (not bas[1] or not haut[0]): yaVitrage = False
                            #if (hp>=hj) and (not m.s.sol.incliné): yaSol = False # même pb qu'en dessous ! (si pentu faudra voir !)
                            #if (hs2<=hj) and (not m.s.plafond.incliné): yaPlafond = False # pb pour couvrir plafond et combles ! (et si pentu faudra voir !)
                        else:
                            if E.Y_ZBUFFER:
                                bas, haut = self.zBuf.yBuf.màj(x1,x2,min(ys1,ys2),max(yp1,yp2),max(ys1,ys2),min(yp1,yp2), False)
                                if (not m.portail) and (not m.s.étage) and (m.est_Opaque()): self.zBuf.yBuf.màj(x1,x2) # panneaux => rideaux fermés
                            else: bas, haut = (True,True),(True,True)
                            if (not bas[0]) or (hs>=hj and not m.s.sol.incliné): yaSol = False # sol caché par la fenêtre en bas (si pentu faudra voir !)
                            if not bas[1]: yaMur = False # mur caché par la fenêtre en bas
                            if not haut[0]: yaMur = False # mur caché par la fenêtre en haut
                            if (not m.s.ciel) and ((not haut[1]) or (hp<=hj and not m.s.plafond.incliné)): yaPlafond = False # plafond caché par la fenêtre en haut (si pentu faudra voir !)
                        # "mur" (bas) à tracer ? (TEST 5 finalisé)
                        if yaMur or yaSol or yaPlafond: # si un élément présent on trace
                            cat = (yaMur, yaSol, yaPlafond and not(m.marche), False) # pas de plafond si marche
                            t = T.Tracé_Quads(m,cat, x1,ys1,yp1,x2,ys2,yp2, (X1,X2), (k1,k2), (sk1,sk2), self.M.j)
                            self.T.tracés.append(t)
                        if m.marche: # pour l'élément du haut
                            if yaMurHaut or yaPlafond:
                                cat = (yaMurHaut, False, yaPlafond, True, False) # pas de sol puisque marche
                                t = T.Tracé_Quads(m,cat, x1,ys1b,yp1b,x2,ys2b,yp2b, (X1,X2), (k1,k2), (sk1,sk2), self.M.j)
                                self.T.tracés.append(t)
                            if yaVitrage:
                                cat = (True, False, False, True, True) # pas de sol puisque marche
                                t = T.Tracé_Quads(m,cat, x1,yp1,ys1b,x2,yp2,ys2b, (X1,X2), (k1,k2), (sk1,sk2), self.M.j)
                                self.T.tracés.append(t)
            if mur.g != None:
                # faut-il zapper un demi-plan ? (hors champs à D_COLLISION près)
                if (abs(PV) < E.D_COLLISION) or (Ng < 0) or (Nd < 0):
                    self.calc_Scène3D(mur.g)
        else:
            if mur.g != None: self.calc_Scène3D(mur.g)
            if mur.d != None:
                # faut-il zapper un demi-plan ? (hors champs à D_COLLISION près)
                if (abs(PV)<E.D_COLLISION) or (m.calc_PS(self.M.j.ug) > 0) or (m.calc_PS(self.M.j.ud) > 0):
                    self.calc_Scène3D(mur.d)

    def tracer_3D(self):
        # retourne et tri pour grouper les étages
        self.T.tracés = list(reversed(self.T.tracés))
        if E.GROUPER_ETAGES:
            i = 0
            while i < len(self.T.tracés):
                t = self.T.tracés[i]
                if (not t.sprite) and (t.m.s.étage>1):
                    m1 = t.m
                    for j in range(i+1,len(self.T.tracés)):
                        m = self.T.tracés[j]
                        if not t.sprite:
                            m2 = t.m
                            if (i!=j) and (m2.s.étage == m1.s.étage): # même étage : on groupe
                                self.T.tracés.insert(i+1,self.T.tracés.pop(j)) 
                                i += 1
                            elif (m2.s.étage//2 == m1.s.étage//2): # étages correspondants : on continue à explorer
                                pass
                            else: # autre intermédiaire : on arrête
                                break
                            # étages différents : on continue à examiner pour grouper.
                i += 1
        for t in self.T.tracés:
            if t.sprite and E.AFF_SPRITES: # sprites
                self.T.tracer_Sprites(t)
            else:
                mur = t.m
                s = mur.s
                AB, SN = [True,True], [True,True]
                if s.no in self.T.clippésA: AB[1] = False
                if s.no in self.T.clippésB: AB[0] = False
                if s.no in self.T.clippésS: SN[1] = False
                if s.no in self.T.clippésN: SN[0] = False
                t.def_Clips(AB,SN)
                # sol
                if mur.retourné and mur.marche: # sol et plafond convercles de sous-secteurs
                    if t.sol and (not t.en_haut) and (t.yp1>=0 or t.yp2>=0):
                        # sol "couvercle" d'un sous-secteur
                        t.ajout_Sol(s.sol,True)
                    elif t.plafond and (t.en_haut) and (t.ys1<E.Y_RES or t.ys2<E.Y_RES):
                        # plafond "couvercle" d'un sous-secteur
                        t.ajout_Plafond(s.plafond,s.ap,True)
                    elif t.vitrage:
                        # vitrage tracé même à l'envers !
                        t.ajout_Mur()
                else:
                    if (t.ys1>=0 or t.ys2>=0):
                        if (t.sol and mur.normal) or (mur.fenêtre and (not mur.retourné)):
                            # sol "normal"
                            t.ajout_Sol(s.sol)
                        elif (t.mur or t.sol) and mur.sous_secteur and (not t.en_haut):
                            # sol "normal" du secteur parent
                            ss = self.M.secteurs[mur.ss]
                            t.ajout_Sol(ss.sol)
                    # mur
                    if mur.retourné and mur.fenêtre and (mur.s.cf!=None):
                        # mur vers un autre secteur : "sous-sol" ?
                        if t.ys1>=0 or t.ys2>=0: # "sous-sol" comme un sol "couvercle"
                            ss = mur.s
                            t.ajout_Fondation(s.cf,mur.lum)
                    elif t.mur and not mur.fenêtre and (t.ys1!=t.yp1 or t.ys2!=t.yp2):
                        # mur "normal"
                        t.ajout_Mur()
                # plafond
                if t.plafond and (t.yp1<E.Y_RES or t.yp2<E.Y_RES):
                    if (not mur.sous_secteur):
                        # plafond "normal"
                        t.ajout_Plafond(s.plafond,s.ap)
                    elif (t.en_haut and not mur.retourné) or mur.pilier:
                        # plafond "normal" du secteur
                        ss = self.M.secteurs[mur.ss]
                        t.ajout_Plafond(ss.plafond,ap=ss.ap)
                    if (mur.retourné and mur.fenêtre and (s.cf!=None)): # mur vers un autre secteur : "combles"
                        # "combles" comme un plafond
                        ss = mur.s
                        t.ajout_Comble(s.cf,mur.lum)
                # on trace l'ensemble
                self.T.tracer_Quads(t)
        return len(self.T.quads), self.T.no
    def aff_3D(self):
        # lot 1 : canal alpha (sprites et textures alpha)
        gl.glDisable(gl.GL_BLEND)
        gl.glAlphaFunc(gl.GL_EQUAL,1)
        gl.glEnable(gl.GL_ALPHA_TEST)
        self.T.lot.draw()
        # lot 2 : textures avec mélange activé (blending)
        gl.glDisable(gl.GL_ALPHA_TEST)
        gl.glEnable(gl.GL_BLEND);
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        self.T.lot2.draw()
        gl.glDisable(gl.GL_BLEND)
    def stats(self):
        return str(len(self.M.murs)+1)+" "+str(self.nb)