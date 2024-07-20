from pyglet import shapes

from math import sqrt,cos, sin, tan, floor, ceil

import structure as C
import env
E = env.Env()

def redef_Env(env):
    global E
    E = env
    C.redef_Env(E)

class recalc_BSP(env.Exceptions):
    pass

class BSP:
    def __init__(self, liste, x=0, y=0):
        self.n = liste[0]
        if liste[1] != None:
            self.g = BSP(liste[1])
        else:
            self.g = None
        if liste[2] != None:
            self.d = BSP(liste[2])
        else:
            self.d = None
    def retourner(self):
        self.g, self.d = self.d, self.g # nécessaire !
        self.n.retourner()
    def ret_Liste(self):
        if self.g != None:
            if type(self.g)==list: bsp_g = self.g
            else: bsp_g = self.g.ret_Liste()
        else: bsp_g = []
        if self.d != None:
            if type(self.d)==list: bsp_d = self.d
            else: bsp_d = self.d.ret_Liste()
        else: bsp_d = []
        return [str(self.n.no)+"("+str(self.n.s.no)+")",bsp_g,bsp_d]
    def ret_Taille(self):
        if self.g == None: tg = 0
        else: tg = self.g.ret_Taille()
        if self.d == None: td = 0
        else: td = self.d.ret_Taille()
        return 1+tg+td
    def ret_Hauteur(self, p=0):
        if self.g == None: tg = 0
        else: tg = self.g.ret_Hauteur(max(0,p-1))
        if self.d == None: td = 0
        else: td = self.d.ret_Hauteur(max(0,p-1))
        if p==0: return 1+max(tg,td)
        else: return (tg,td)
        
class Monde:
    def __init__(self, struct, murs0, joueur, lot, env=None):
        global E
        self.debug = E.DEBUG
        if env != None: E = env
        self.S = struct
        self.j = joueur
        self.lot = lot
        self.secteurs = self.S.ss
        self.murs2D=[None]
        self.murs_retournés = []
        self.init_Eclairage()
        self.init_Portails()
        self.init_Exclu()
        self.init_Marches()
        self.init_Jointures()
        # construction du BSP
        self.murs0 = [self.secteurs[mur0[0]].murs[mur0[1]] for mur0 in murs0 if mur0[0] in self.S.ss]
        while True:
            self.murs = self.murs0[1:]
            for no,s in sorted(self.secteurs.items()):
                self.murs += [mur for mur in s.murs if mur not in self.murs0]
            try:
                self.bsp = self.ret_BSP(self.murs0[0], self.murs)
                break
            except recalc_BSP:
                if self.debug: print(" # exception (recalc_BSP) #")
        if self.debug>=E.DEBUG_1: print(self.bsp.ret_Liste())
        self.secteur = None

    def ret_BSP(self, mur0, murs):
        debug = self.debug
        murs_g, murs_d = [], []
        for m in murs:
            if debug >= E.DEBUG_2: print(mur0.x1,mur0.y1,mur0.x2,mur0.y2," / ",m.x1,m.y1,m.x2,m.y2,end=" * ")
            v1 = (m.x1-mur0.x1,m.y1-mur0.y1)
            v2 = (m.x2-mur0.x1,m.y2-mur0.y1)
            PV1, PV2 = mur0.calc_PV(v1), mur0.calc_PV(v2)
            if PV1 < 0 and PV2 > 0:
                if self.debug >= E.DEBUG_2: print("mur coupé ! (par derrière)",end=" ")
                k = m.calc_PS(v1)/m.calc_PS(mur0.u)
                x = mur0.x1 + k*mur0.u[0]
                y = mur0.y1 + k*mur0.u[1]
                if self.debug >= E.DEBUG_2: print("intersection : ({},{})".format(x,y))
                self.secteurs[m.s.no].couper_Mur(m.no,x,y,self)
                raise recalc_BSP
            elif PV1 > 0 and PV2 < 0:
                if self.debug >= E.DEBUG_2: print("mur coupé ! (par devant)",end=" ")
                k = m.calc_PS(v1)/m.calc_PS(mur0.u)
                x = mur0.x1 + k*mur0.u[0]
                y = mur0.y1 + k*mur0.u[1]
                if self.debug >= E.DEBUG_2: print("intersection : ({},{})".format(x,y),"n°",m.no)
                self.secteurs[m.s.no].couper_Mur(m.no,x,y,self)
                raise recalc_BSP
            elif PV1 == 0 and PV2 == 0:
                if debug: print("murs confondus : {}({}) et {}({})".format(mur0.no,mur0.s.no,m.no,m.s.no))
                if (m.s.normal) ^ (mur0.calc_PS(m.N)>0): murs_g.append(m) # à gauche !
                else: murs_d.append(m) # à droite !
                #if (mur0.calc_PS(m.N)>0 and mur0.marche and m.marche) or mur0.fenêtre: murs_g.append(m) 
                #else: murs_d.append(m) 
            elif PV1 <= 0 and PV2 <= 0:
                if debug >= E.DEBUG_2: print("un mur à droite")
                murs_d.append(m)
            elif PV1 >= 0 and PV2 >= 0:
                if debug >= E.DEBUG_2: print("un mur à gauche")
                murs_g.append(m)

        bsp = BSP([mur0, None, None],self.j.x,self.j.y)
        if murs_g != []: bsp.g = self.ret_BSP(murs_g[0],murs_g[1:])
        if murs_d != []: bsp.d = self.ret_BSP(murs_d[0],murs_d[1:])
        return bsp

    def tracer_2D(self, r, decal=(0,0), mur=None, nouv=True):
        if mur == None:
            mur = self.bsp
        elif type(mur)== list:
            return
        m = mur.n
        if m.c != None:
            shape = shapes.Line(r*(m.x1+decal[0]),r*(m.y1+decal[1]),r*(m.x2+decal[0]),r*(m.y2+decal[1]), color=m.c, batch = self.lot)
            if m.portail: shape.opacity = 50
            if nouv:
                self.murs2D = [None,shape]
                # et le mur0
                for m0 in self.murs0:
                    if m0.u[0] != 0:
                        t1 = -(decal[0]+m0.x1)/m0.u[0]
                        t2 = (E.X_RES/r-decal[0]-m0.x1)/m0.u[0]
                        x1, y1, x2, y2 = -decal[0], m0.y1+m0.u[1]*t1, E.X_RES/r-decal[0], m0.y1+m0.u[1]*t2
                    else:
                        t1 = -(decal[1]+m0.y1)/m0.u[1]
                        t2 = (E.Y_RES/r-decal[1]-m0.y1)/m0.u[1]
                        x1, y1, x2, y2 = m0.x1+m0.u[0]*t1, -decal[1], m0.x1+m0.u[0]*t2, E.Y_RES/r-decal[1]
                    shape = shapes.Line(r*(x1+decal[0]),r*(y1+decal[1]),r*(x2+decal[0]),r*(y2+decal[1]), color=E.C['jaune'], batch = self.lot)
                    #shape.opacity = 50   
                    self.murs2D.append(shape)    
            else:
                self.murs2D.append(shape)
        if (mur.g != None) and (type(mur.g) != list):
            self.tracer_2D(r, decal, mur.g, False)
        if (mur.d != None) and (type(mur.d) != list):
            self.tracer_2D(r, decal, mur.d, False)
    
            
    def allumer(self, no):
        s = self.secteurs[no]
        état = s.allumer()
        for no,murs in s.conn.items():
            s2 = self.secteurs[no]
            if murs == None: # on allume le secteur connecté ...
                s2.allumer()
            else: # ... ou bien les murs connectés sont éclairés
                for m in murs:
                    print(état,end="_")
                    s2.murs[m].lum.lumin += s.lumin*(état-0.5)*2  # état=1 : +lumin / état=0 : -lumin

    def init_Eclairage(self):
        for no in self.secteurs:
            s = self.secteurs[no]
            #lumin = s.lumin*(s.allumé-0.5)*2
            lumin = s.lumin*s.allumé
            if s.ap != None: # ciel : jour/nuit
                s.plafond.c = (255*s.allumé,255*s.allumé,255*s.allumé)
            else:
                s.plafond.lum.lumin = lumin
                s.sol.lum.lumin = lumin
                déconnectés = []
                for no2,murs in s.conn.items(): # on connecte les murs des autres secteurs ...
                    try:
                        s2 = self.secteurs[no2]
                        if murs == None:
                            s2.allumé = s.allumé
                        else:
                            for m in murs:
                                if m == None: s2.allumer()
                                else:
                                    s2.murs[m].lum.lumin += s.lumin*(s.allumé-0.5)*2
                                    s2.murs[m].lum.ombre = s.ombre
                                    s2.murs[m].conn.append(no) 
                    except: # le secteur a disparu ?! ...
                        déconnectés.append(no2) # ... on enlève la connexion
                for no in déconnectés:
                    del s.conn[no]

    def init_Portails(self): # permet de supprimer les portails vers des secteurs supprimés
        for no in self.secteurs:
            s = self.secteurs[no]
            if s.portails != None:
                for p in s.portails.keys():
                    if s.portails[p] not in self.secteurs:
                        if E.DEBUG>=E.DEBUG_1: print("portail supprimé :",no,"vers",s.portails[p])
                        s.portails[p] = s.ss # on place le sous secteur par défaut
                        s.murs[p].ss = s.ss # idem pour le mur

    def init_Exclu(self): # permet de supprimer les exclusions de ou vers des secteus supprimés
        for no in self.S.exclu.keys():
            if no not in self.secteurs: del self.S.exclu[no]
            else:
                l = self.S.exclu[no]
                self.S.exclu[no] = [s for s in l if s in self.secteurs]
                if len(l) != len(self.S.exclu[no]) and E.DEBUG>=E.DEBUG_1: print("liste exclu mise à jour :",l,"vers",self.S.exclu)

    def init_Marches(self): # permet d'initialiser la hauteur des fenêtres des marches ainsi que les t des textures du haut
        for no in self.secteurs:
            s = self.secteurs[no]
            if s.marche:
                s.h = self.calc_HauteurPlafond(s) - self.calc_HauteurSol(s)
                for m in s.murs:
                    if m.texb!=None and (m.texb.t1==None or m.texb.t2==None):
                        k = (m.tex.t2-m.tex.t1)/s.h_sol
                        m.texb.t1 = m.tex.t2 + k*s.h
                        m.texb.t2 = m.texb.t1 - k*s.h_plafond

    def init_Jointures(self): # permet de caler le s et le t des textures pour jointures
        for mur,mur0 in self.S.jointures.items():
            s0, s = self.secteurs[mur0[0]], self.secteurs[mur[0]]
            no = mur[1]
            m0, m = s0.murs[mur0[1]], s.murs[no]
            m.jointure = True
            if s0.marche:
                k = (m0.tex.t2-m0.tex.t1)/s0.h_sol
            else:
                k = (m0.tex.t2-m0.tex.t1)/s0.h
            t1 = m0.tex.t1
            if s.marche:
                t2 = t1 + k*s.h_sol
                t1b = t2 + k*s.h
                t2b = t1b - k*s.h_plafond
            else:
                t2 = t1 + k*s.h
            while m.jointure:
                ds = m.tex.s2-m.tex.s1
                m.tex.s1 = m0.tex.s2
                m.tex.s2 = m.tex.s1 + ds
                m.tex.t1, m.tex.t2 = t1, t2
                if s.marche and (m.texb != None):
                    dsb = m.texb.s2-m.texb.s1
                    m.texb.s1 = m0.tex.s2
                    m.texb.s2 = m.texb.s1 + dsb
                    m.texb.t1, m.texb.t2 = t1b, t2b
                m0 = m
                no = (no+1)%len(s.murs)
                m = s.murs[no]

    def aff_2D(self):
        self.lot.draw()

    def calc_HauteurSol(self, s): # socle seulement (sans dénivelés)
        if s.normal: return s.h_sol # secteur parent
        ss = self.secteurs[s.ss] # ... sinon sous secteur parent
        return s.h_sol + self.calc_HauteurSol(ss)

    def calc_HauteurPlafond(self, s):
        if s.normal: return s.h_plafond # secteur parent
        ss = self.secteurs[s.ss] # ... sinon sous secteur parent
        return s.h_plafond + self.calc_HauteurPlafond(ss)

    def calc_HauteurPied(self): # hauteur sol avec dénivelé
        s = self.secteurs[self.j.s]
        return self.calc_HauteurSol(s) + s.calc_Dénivelé(self.j.x,self.j.y)

    def ret_SecteursParents(self, s):
        if s.normal: return [s]
        return self.ret_SecteursParents(self.secteurs[s.ss]) + [s]
        
        
        
                