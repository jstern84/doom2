from math import sqrt, cos, sin, tan, atan, floor, ceil
from copy import deepcopy

import tracer as T
import sprites
import textures

import env
E = env.Env()

def redef_Env(env):
    global E
    E = env
    T.redef_Env(E)
    sprites.redef_Env(E)

class Structure():
    def __init__(self, secteurs={}, env=None):
        global E
        if env != None: E = env
        self.ss = secteurs
        self.exclu = {}
        self.clips = {}
        self.jointures = {}
        self.nb_étages = 0
        self.I = sprites.Sprites(E)
        self.X = textures.Textures(E)
    def ajout_Etages(self, étage1, étage2):
        self.nb_étages += 2 # no 0 et 1 reservés
        for no in étage1: # no pair pour le bas
            self.ss[no].étage = self.nb_étages
        for no in étage2: # no impair pour le haut
            self.ss[no].étage = self.nb_étages+1
    def def_Etages(self, étages):
        for no in étages:
            self.ss[no].étage = True
    def ajout_ExcluIn(self, exclu): # le secteur-clé est exclu vu depuis les différents secteurs-valeurs
        for (s1,ss) in exclu.items():
            if s1 in self.ss:
                for s2 in ss:
                    if s2 in self.ss: # (attention au secteurs supprimés)
                        if (s1 in self.exclu): self.exclu[s1].append(s2)
                        else: self.exclu[s1] = [s2]
    def ajout_ExcluOut(self, exclu): # les différents secteurs-valeurs sont exclus depuis le secteur-clé
        for (s1,ss) in exclu.items():
            if s1 in self.ss:
                for s2 in ss:
                    if s2 in self.ss: # (attention au secteurs supprimés)
                        if (s2 in self.exclu) and (not s1 in self.exclu[s2]): self.exclu[s2].append(s1)
                        elif (s2 not in self.exclu): self.exclu[s2] = [s1]
    def ajout_ExcluEtage(self, étage, vu_depuis):
        for s1 in étage:
            self.ajout_ExcluIn({s1:vu_depuis})
    def ajout_Exclu(self, étage1, étage2): # pour aussi exclure du X zBuffer (attention au secteurs supprimés)
        for s1 in étage1:
            self.ajout_ExcluIn({s1:étage2})
            self.ajout_ExcluOut({s1:étage2})
    def ajout_Clip(self, vu_depuis, vu_àtravers, côté, secteurs):
        for s in vu_depuis:
            clé = (s,vu_àtravers[0])
            self.clips[clé] = Clip(vu_àtravers[1],côté,secteurs)
            if E.DEBUG>=E.DEBUG_2: print("clip:",s,vu_àtravers,côté,secteurs)
    def ajout_Jointures(self, jointures): # joint la texture de mur à celle de mur0
        for i in range(len(jointures)-1):
            self.jointures[jointures[i+1][0:2]] = (jointures[i][0],jointures[i][-1]) 
    def def_ArrièrePlan(self, secteurs, ap):
        for no in secteurs:
            if no in self.ss:
                s = self.ss[no]
                s.ap = ap
                s.ciel = True
    def def_Vitrage(self, mur, tex):
        self.ss[mur[0]].murs[mur[1]].def_Vitrage(tex)

    def a_Texture(self, mur):
        a_tex = (mur.tex!=None) or (mur.texb!=None) or (mur.texc!=None) or (mur.texs!=None) or (mur.texp!=None)
        if mur.sous_secteur: # et le secteur parent ?
            s = self.ss[mur.ss]
            a_tex = a_tex or (s.sol.tex!=None) or (s.plafond.tex!=None)
        return a_tex

class Clip():
    def __init__(self, mur, côté, secteurs):
        self.mur = mur
        self.côté = côté
        self.secteurs = secteurs

class Mur:
    def __init__(self, xA, yA, xB, yB, secteur=None, no=-1, portail=False, sous_secteur=None, couleur=None, lumière=None, h=((0,0),(0,0))):
        self.ss = sous_secteur
        self.s = secteur
        self.no = no
        self.c = couleur # None si pas de mur
        self.conn = [] # secteurs connectés
        self.x1, self.y1 = xA, yA
        self.x2, self.y2 = xB, yB
        self.hs1, self.hs2 = h[0][0], h[0][1]
        self.hp1, self.hp2 = h[1][0], h[1][1]
        self.dx = xB - xA
        self.dy = yB - yA
        self.l = sqrt(self.dx**2+self.dy**2)
        self.u = (self.dx/self.l, self.dy/self.l)
        Nx, Ny = yB-yA, xA-xB
        l = sqrt(Nx**2+Ny**2)
        self.N = (Nx/l,Ny/l)
        #  texture et lumière
        self.lum = lumière
        self.lum.N = self.N + (0,) # on a besoin de N pour le Soleil 
        # type de mur
        self.portail = portail
        self.sous_secteur = (not secteur.normal)
        self.fenêtre = portail and secteur.normal
        self.pilier = secteur.pilier
        self.marche = secteur.marche
        self.normal = (not portail) and secteur.normal
        self.retourné = False
        self.biseauté = (self.hs1!=0 or self.hs2!=0 or self.hp1!=0 or self.hp2!=0)
        # texture
        self.tex = None 
        self.jointure = False
        self.vitrage = False
        self.texb, self.texc = None, None 
        self.texs, self.texp = None, None

    def def_Texture(self, tex, répéter=False, s1=0, t1=0, texb=None):
        self.tex = tex
        self.texb = texb
        self.tex.s1 = s1
        self.tex.t1 = t1
        if self.marche and (texb != None):
            self.texb.s1 = s1
            self.texb.t1 = 0
        if répéter:
            self.tex.s2 = self.tex.s1 + self.l/E.COEF_MOTIF
            if self.marche and (texb != None):
                self.tex.t2 = self.tex.t1 + self.s.h_sol/E.COEF_MOTIF
                self.texb.t2 = self.texb.t1 - self.s.h_plafond/E.COEF_MOTIF
            else:
                self.tex.t2 = self.tex.t1 + self.s.h/E.COEF_MOTIF
        else:
            self.tex.s2, self.tex.t2 = 1, 1
            if self.marche and (texb != None): self.texb.s2, self.texb.t2 = 1, 1

    def def_Vitrage(self, tex, répéter=False, s1=0, t1=0):
        self.vitrage = True
        self.texc = tex
        self.texc.s1 = s1
        self.texc.t1 = t1
        if répéter:
            self.texc.s2 = self.texc.s1 + self.l/E.COEF_MOTIF
        else: self.texc.s2 = 1
        self.texc.t2 = 1

    def est_Opaque(self):
        return (self.c!=None) and (self.tex==None or self.tex.opaque)

    def calc_PS(self, v):
        return round(self.N[0]*v[0]+self.N[1]*v[1],E.NB_DECIMALES)
    def calc_PV(self, v):
        return round(self.u[0]*v[1]-self.u[1]*v[0],E.NB_DECIMALES)
    def ret_PV(self, v):
        return (self.u[1]*v[2], -self.u[0]*v[2], self.u[0]*v[1]-self.u[1]*v[0])
    def ret_PS(self, v):
        return round(self.u[0]*v[0]+self.u[1]*v[1],E.NB_DECIMALES)

    def retourner(self):
        self.retourné = not self.retourné
        self.x1, self.x2 = self.x2, self.x1
        self.y1, self.y2 = self.y2, self.y1
        self.hs1, self.hs2 = self.hs2, self.hs1
        self.hp1, self.hp2 = self.hp2, self.hp1
        self.dx = -self.dx
        self.dy = -self.dy
        self.u = [-k for k in self.u]
        self.N = [-k for k in self.N]
        if self.tex!=None: self.tex.retourner()
        if self.texb!=None: self.texb.retourner()
        if self.texc!=None: self.texc.retourner()
        if self.texs!=None: self.texs.retourner()
        if self.texp!=None: self.texp.retourner()

    def a_droite(self, x, y):
        v1 = [self.x1-x, self.y1-y]
        v2 = [self.x2-x, self.y2-y]
        PV, PV2 = self.calc_PV(v1), self.calc_PV(v2)
        if abs(PV2) > abs(PV): return (PV2 > 0) ^ self.retourné
        else: return (PV > 0) ^ self.retourné

class Surface(): # sol ou plafond
    def __init__(self, secteur, couleur=None, lumière=None, pente=0, plafond=False):
        self.plafond = plafond # False si c'est un sol
        self.s = secteur
        self.mur0 = secteur.murs[0]
        self.c = couleur
        self.lum = lumière
        self.pente = round(pente,E.NB_DECIMALES)
        self.incliné = (pente != 0)
        # calcul de N
        if secteur.marche: k = -1 # on retourne Nz pour une marche
        else: k = 1
        if plafond: p = 1 # on retourne N pour un plafond
        else: p = -1
        if pente == 0:
            self.N = (0,0,-p)
        else:
            Nz = cos(atan(pente)) # composante verticale
            q = sqrt(1-Nz**2) # inverse de la norme de la composante horizontale
            self.U = (p*self.mur0.N[0]*q, p*self.mur0.N[1]*q, p*k*Nz) # vecteur unitaire colinéaire à la pente
            self.N = self.mur0.ret_PV(self.U)
        self.lum.N = self.N
        # texture
        self.tex = None
        self.x0, self.y0 = 0, 0
    def calc_Dénivelé(self, v, signé=False):
        d = self.mur0.calc_PV((v[0]-self.mur0.x1,v[1]-self.mur0.y1)) # calcul de la distances au mur 0
        if signé:
            if self.mur0.retourné: return -d*self.pente
            return d*self.pente
        return abs(d)*self.pente # calculs des dénivelés
    def def_Texture(self, tex, v0=0, échelle=1):
        self.tex = tex
        x0, y0 = self.s.v[v0][0], self.s.v[v0][1]
        self.x0, self.y0 = x0, y0
        self.tex.échelle = échelle
        for m in self.s.murs:
            if self.plafond:
                m.texp = tex.dupliquer()
                t = m.texp
            else:
                m.texs = tex.dupliquer()
                t = m.texs
            t.s1, t.t1 = self.calc_t2Coords(m.x1,m.y1)
            t.s2, t.t2 = self.calc_t2Coords(m.x2,m.y2)
    def calc_t2Coords(self, x, y):
        s, t = (x-self.x0)*self.tex.échelle/E.COEF_MOTIF, (y-self.y0)*self.tex.échelle/E.COEF_MOTIF
        return s,t

class Secteur:
    def __init__(self, v, h_sol, h_plafond, no, couleurs_murs=None, couleur_sol=None, couleur_plafond=None, sous_secteur=None, portails=None, couleur_fondation=E.COUL_FOND, lumin=0, allumé=0, conn={}, brillance=0, ombre=0, soleil=True, pentes=(0,0)):
        self.portails = portails
        self.pilier = (portails == None and sous_secteur != None)
        self.marche = (portails != None and sous_secteur != None)
        self.normal = (sous_secteur == None)
        self.étage = False
        self.ciel = False
        if self.marche:
            for i in range(len(v)):
                if i not in self.portails:
                    self.portails[i] = sous_secteur # si pas de sous-secteurs particuliers
        #self.ss = sous_secteur
        self.no = no
        self.cf = couleur_fondation
        self.ap = None
        self.lumin = lumin
        self.allumé = allumé
        self.conn = conn # murs connectés au secteur pour interrupteur lumière
        self.ombre = ombre
        self.h_sol = h_sol
        self.h_plafond = h_plafond
        self.ss = sous_secteur
        self.bsp=None
        self.v = v
        v1, v2 = v[-1], v[0]
        no = 0
        if self.marche:
            ss = self.portails[no]
            self.h = None # il faudra initialiser avec le secteur parent
        else:
            ss = sous_secteur
            self.h = self.h_plafond-self.h_sol
        lum = T.Lumière(0, brillance, ombre)
        mur0 = Mur(v1[0],v1[1],v2[0],v2[1],self,no,(portails != None) and (no in self.portails),ss,couleurs_murs[no],lum)
        self.murs = [mur0]
        self.sol = Surface(self, couleur_sol, T.Lumière(0, brillance, ombre), pentes[0], False) 
        self.plafond = Surface(self, couleur_plafond, T.Lumière(0, brillance, ombre), pentes[1], True) # On inverse N pour un plafond
        v1 = v2
        hs, hp = (0,0), (0,0)
        for v2 in v[1:]:
            no += 1
            if self.marche: ss = self.portails[no]
            else: ss = sous_secteur
            if self.sol.incliné:
                hs = (hs[1],self.sol.calc_Dénivelé(v2))
            if self.plafond.incliné:
                hp = (hp[1],self.plafond.calc_Dénivelé(v2))
            lum = T.Lumière(0, brillance, ombre)
            self.murs.append(Mur(v1[0],v1[1],v2[0],v2[1],self,no,(portails != None) and (no in self.portails),ss,couleurs_murs[no],lum, (hs,hp)))
            v1 = v2
    def def_TextureJointe(self, m, n, tex, texb=None): # texturage joint de n murs à partir du no m
        self.murs[m].def_Texture(tex,True, texb=texb)
        s1 = self.murs[m].tex.s2
        for k in range(m+1,m+n):
            mur = self.murs[k%len(self.murs)]
            if texb != None: texb = texb.dupliquer()
            mur.def_Texture(tex.dupliquer(), True, s1, 0, texb)
            mur.jointure = True
            s1 = mur.tex.s2

    def couper_Mur(self, no, x, y, monde):
        murs = []
        for m in reversed(self.murs): # reversed nécessaire pour la renumérotation des connexions lumière
            if m.no < no:
                murs.append(m)
            elif m.no > no:
                for no2 in m.conn: # on rétablit toutes les connexions lumière
                    s = monde.secteurs[no2]
                    s.conn[self.no] = [i+1 if i==m.no else i for i in s.conn[self.no]]
                m.no += 1
                murs.append(m)
            else:
                if self.sol.incliné: hs = self.sol.calc_Dénivelé((x,y))
                else: hs = 0
                if self.plafond.incliné: hp = self.plafond.calc_Dénivelé((x,y))
                else: hp = 0
                mur1 = Mur(m.x1, m.y1, x, y, self, no, m.portail, m.ss, m.c, m.lum, ((m.hs1,hs),(m.hp1,hp)))
                mur2 = Mur(x, y, m.x2, m.y2, self, no+1, m.portail, m.ss, m.c, deepcopy(m.lum), ((hs,m.hs2),(hp,m.hp2)))
                if m.tex != None:
                    s = m.tex.s1 + (m.tex.s2-m.tex.s1)*mur1.l/m.l
                    mur1.tex, mur2.tex = m.tex.dupliquer(), m.tex.dupliquer()
                    mur1.tex.s1, mur1.tex.s2, mur2.tex.s1, mur2.tex.s2 = m.tex.s1, s, s, m.tex.s2
                    mur1.tex.t1, mur1.tex.t2, mur2.tex.t1, mur2.tex.t2 = m.tex.t1, m.tex.t2, m.tex.t1, m.tex.t2
                    mur1.jointure, mur2.jointure = m.jointure, m.jointure
                if m.marche:
                    if m.texb != None:
                        sb = m.texb.s1 + (m.texb.s2-m.texb.s1)*mur1.l/m.l
                        mur1.texb, mur2.texb = m.texb.dupliquer(), m.texb.dupliquer()
                        mur1.texb.s1, mur1.texb.s2, mur2.texb.s1, mur2.texb.s2 = m.texb.s1, sb, sb, m.texb.s2
                        mur1.texb.t1, mur1.texb.t2, mur2.texb.t1, mur2.texb.t2 = m.texb.t1, m.texb.t2, m.texb.t1, m.texb.t2
                    if m.texc != None:
                        sc = m.texc.s1 + (m.texc.s2-m.texc.s1)*mur1.l/m.l
                        mur1.texc, mur2.texc = m.texc.dupliquer(), m.texc.dupliquer()
                        mur1.texc.s1, mur1.texc.s2, mur2.texc.s1, mur2.texc.s2 = m.texc.s1, sc, sc, m.texc.s2
                        mur1.texc.t1, mur1.texc.t2, mur2.texc.t1, mur2.texc.t2 = m.texc.t1, m.texc.t2, m.texc.t1, m.texc.t2
                if m.texs != None:
                    ss = m.texs.s1 + (m.texs.s2-m.texs.s1)*mur1.l/m.l
                    ts = m.texs.t1 + (m.texs.t2-m.texs.t1)*mur1.l/m.l
                    mur1.texs, mur2.texs = m.texs.dupliquer(), m.texs.dupliquer()
                    mur1.texs.s1, mur1.texs.s2, mur2.texs.s1, mur2.texs.s2 = m.texs.s1, ss, ss, m.texs.s2
                    mur1.texs.t1, mur1.texs.t2, mur2.texs.t1, mur2.texs.t2 = m.texs.t1, ts, ts, m.texs.t2
                if m.texp != None:
                    sp = m.texp.s1 + (m.texp.s2-m.texp.s1)*mur1.l/m.l
                    tp = m.texp.t1 + (m.texp.t2-m.texp.t1)*mur1.l/m.l
                    mur1.texp, mur2.texp = m.texp.dupliquer(), m.texp.dupliquer()
                    mur1.texp.s1, mur1.texp.s2, mur2.texp.s1, mur2.texp.s2 = m.texp.s1, sp, sp, m.texp.s2
                    mur1.texp.t1, mur1.texp.t2, mur2.texp.t1, mur2.texp.t2 = m.texp.t1, tp, tp, m.texp.t2
                mur1.conn, mur2.conn = m.conn, deepcopy(m.conn)
                murs.append(mur2)
                murs.append(mur1)
                for no2 in m.conn: # on rétablit toutes les connexions lumière
                    s = monde.secteurs[no2]
                    s.conn[self.no].append(no+1)

        self.murs = list(reversed(murs))


    def allumer(self):
        self.allumé = 1-self.allumé
        if self.ap!=None: # ciel : jour/nuit
            self.plafond.c = (255*self.allumé,255*self.allumé,255*self.allumé)
        else:
            lumin = self.lumin*(self.allumé-0.5)*2 # état=1 : +lumin / état=0 : -lumin
            self.plafond.lum.lumin += lumin
            self.sol.lum.lumin += lumin
            for m in self.murs: # on allume tous les murs
                m.lum.lumin += lumin 
        return self.allumé

    def calc_Dénivelé(self, x, y):
        if self.sol.incliné:
            return self.sol.calc_Dénivelé((x,y))
        else:
            return 0

