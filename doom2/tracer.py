from math import pi,atan,sqrt,cos
import pyglet
from pyglet import shapes, gl
from colorsys import rgb_to_hsv, hsv_to_rgb, rgb_to_hls, hls_to_rgb

import structure as C
import textures as X
import env

E = env.Env()
def redef_Env(env):
    global E
    E = env

class Tracer():
    def __init__(self, textures):
        self.tracés = []
        self.A, self.B = True, True
        self.N, self.S = True, True
        # groupe no=0 pour les cadres filaires
        self.groupefil = Groupe0(0)
        self.groupefil.fil = True
        # autres groupes
        self.no = 1
        self.z = 0
        self.groupe0 = Groupe0(self.no)
        self.groupeA, self.groupeB = GroupeA(self.no), GroupeB(self.no)
        self.groupeS, self.groupeN = GroupeS(self.no), GroupeN(self.no)
        self.groupeAS, self.groupeAN = GroupeAS(self.no), GroupeAN(self.no)
        self.groupeBS, self.groupeBN = GroupeBS(self.no), GroupeBN(self.no)
        self.groupe = self.groupe0
        self.quads = []
        self.sprites = []
        self.textures = textures
        self.lot = pyglet.graphics.Batch()
        self.lot2 = pyglet.graphics.Batch()
        self.clippésA, self.clippésB = [], []
        self.clippésS, self.clippésN = [], []
        self.étages = []
    def tracer_Quads(self, t):
        for q in t.quads:
            if (E.MODE_DESSIN != 0): # on remplit 
                if (q.lum != None and q.c != None): c4 = q.lum.calc_Couleur(q.c, E.SOLEIL, q.Zs)
                else: c4 = (E.COUL_TEX)*4
                self.clip(t)
                if E.MODE_DESSIN == 2:
                    self.groupe.fil = False
                if (q.tex == None):
                    q.def_z(self.z)
                    self.z += E.DZ
                    self.lot.add(4, gl.GL_QUADS, self.groupe, ('v3f/static',q.v), ('c3B/static',c4))
                else:
                    q.def_z(self.z)
                    self.z += E.DZ
                    texturegroupe = pyglet.graphics.TextureGroup(q.tex.texture,self.groupe)
                    if q.tex.mélange:
                        lot = self.lot2
                        texturegroupe = pyglet.graphics.TextureGroup(q.tex.texture)
                    else:
                        lot = self.lot
                        texturegroupe = pyglet.graphics.TextureGroup(q.tex.texture,self.groupe)
                    lot.add(4, gl.GL_QUADS, texturegroupe, ('v3f/static',q.v), ('c3B/static',c4), ('t4f/static',q.t4coords))
            if E.MODE_DESSIN!=1 and q.c!=None:#(not sans_bordures) and mode != 1:
                r = min(round(q.c[0]*1.5),255)
                v = min(round(q.c[1]*1.5),255)
                b = min(round(q.c[2]*1.5),255)
                #self.clip(t)
                self.lot.add(4, gl.GL_QUADS, self.groupefil, ('v3f/static',q.v), ('c3B/static',(r,v,b)*4))
            self.quads.append(q)
    def tracer_Sprites(self, t):
        self.groupe.fil = False
        for s in t.sprites:
            t = pyglet.sprite.Sprite(s.image, s.X, s.Y)
            t.scale = s.échelle
            v = list(t._vertex_list.vertices)
            v.insert(2,self.z)
            v.insert(5,self.z)
            v.insert(8,self.z)
            v.insert(11,self.z)
            vertex_format = 'v3f/%s' % t._usage
            self.lot.add(4, gl.GL_QUADS, t._group, (vertex_format,tuple(v)), ('c4B',t._vertex_list.colors), ('t3f', t._texture.tex_coords))
            self.sprites.append(t)
            self.z += E.DZ
    def nouv_Groupe(self):
        self.no += 1
        self.groupe0 = Groupe0(self.no)
        self.groupeA, self.groupeB = GroupeA(self.no), GroupeB(self.no)
        self.groupeS, self.groupeN = GroupeS(self.no), GroupeN(self.no)
        self.groupeAS, self.groupeAN = GroupeAS(self.no), GroupeAN(self.no)
        self.groupeBS, self.groupeBN = GroupeBS(self.no), GroupeBN(self.no)
        groupe_p = self.groupe
        if type(self.groupe) == Groupe0:
            self.groupe = self.groupe0
        else:
            if type(self.groupe) == GroupeA: 
                self.groupe = self.groupeA
                self.groupe.x = groupe_p.x
            elif type(self.groupe) == GroupeB:
                self.groupe = groupeB
                self.groupe.x = groupe_p.x
            elif type(self.groupe) == GroupeS:
                self.groupe = groupeS
                self.groupe.plan = groupe_p.plan
            elif type(self.groupe) == GroupeN:
                self.groupe = groupeN
                self.groupe.plan = groupe_p.plan
            else:
                if type(self.groupe) == GroupeAS: self.groupe = groupeAS
                elif type(self.groupe) == GroupeAN: self.groupe = groupeAN
                elif type(self.groupe) == GroupeBS: self.groupe = groupeBS
                elif type(self.groupe) == GroupeBN: self.groupe = groupeBN
                self.groupe.x = groupe_p.x
                self.groupe.plan = groupe_p.plan

    def clip(self, t):
        if (t.A,t.B,t.S,t.N)!=(self.A,self.B,self.S,self.N) or (E.MODE_DESSIN==2): # changement de groupe
            self.z += E.DZ
            self.A, self.B = t.A, t.B
            self.S, self.N = t.S, t.N
            if (t.A,t.B,t.S,t.N) == (True,True,True,True): self.groupe = self.groupe0 # on revient au défaut
            elif t.B == False:
                if t.S == True and t.N == True: self.groupe = self.groupeA
                elif t.N == False:
                    self.groupe = self.groupeAS
                    self.groupe.plan = self.planS
                elif t.S == False:
                    self.groupe = self.groupeAN
                    self.groupe.plan = self.planN    
                self.groupe.x = self.x_clipA
            elif t.A == False:
                if t.S == True and t.N == True:
                    self.groupe = self.groupeB
                elif t.N == False:
                    self.groupe = self.groupeBS
                    self.groupe.plan = self.planS
                elif t.S == False:
                    self.groupe = self.groupeBN
                    self.groupe.plan = self.planN
                self.groupe.x = self.x_clipB
            else: # B et A à True
                if t.N == False:
                    self.groupe = self.groupeS
                    self.groupe.plan = self.planS
                elif self.S == False:
                    self.groupe = self.groupeN
                    self.groupe.plan = self.planN
                else:
                    print("A, B, S et N à False ??")
                    quit()


class Tracé():
    def __init__(self):
        self.sprite = False
class Tracé_Sprites(Tracé): # sprites groupés à tracer
    def __init__(self):
        self.sprite = True
        self.sprites = []
    def ajout_Sprite(self, sprite): # ajout du sprite avec tri par insertion Z
        i=0
        while i<len(self.sprites) and self.sprites[i].Z > sprite.Z:
            i += 1
        self.sprites.insert(i, sprite)
class Tracé_Quads(Tracé):
    def __init__(self, mur,cat, x1,ys1,yp1,x2,ys2,yp2, Zs,Ws=None,Ks=None, joueur=None):
        self.sprite = False
        self.m = mur
        # catégories à tracer
        self.mur = cat[0]
        self.sol = cat[1]
        self.plafond = cat[2]
        self.en_haut = cat[3] # pour mur haut d'une marche
        self.ciel = mur.s.ciel
        self.vitrage = mur.marche and self.en_haut and cat[4]
        self.z1, self.z2 = Zs[0], Zs[1] # profondeurs pour dégradés
        self.w1, self.w2 = Ws[0], Ws[1] # w=R0/z pour interpolation projective des textures
        self.Ks = Ks # proportions du mur coupé à gauche et à droite
        self.x1, self.ys1, self.yp1 = x1, ys1, yp1
        self.x2, self.ys2, self.yp2 = x2, ys2, yp2
        self.quads = []
        self.j = joueur
    def def_Clips(self, AB=(True,True), SN=(True,True)):
        self.A, self.B = AB[0], AB[1]
        self.S, self.N = SN[0], SN[1]        
    def ajout_Mur(self):
        z1, z2 = self.z1/(E.R1+self.z1), self.z2/(E.R1+self.z2) # pseudo-Z pour le dégradé des murs
        Zs = (z1,z1,z2,z2)
        quad = Quad(self.x1,self.ys1,self.yp1,self.x2,self.ys2,self.yp2,self.m.c,self.m.lum,Zs)
        tex,t1b = None,None
        if self.vitrage and (self.m.texc != None): tex = self.m.texc
        elif self.en_haut and (self.m.texb != None): tex =self.m.texb         
        elif self.mur and (self.m.tex != None):
            tex = self.m.tex
            if self.m.normal and self.m.biseauté: # mur sur pente ou sous plafond incliné
                K1, K2 = (self.m.hs1+self.Ks[0]*(self.m.hs2-self.m.hs1))/self.m.s.h, (self.m.hp1+self.Ks[0]*(self.m.hp2-self.m.hp1))/self.m.s.h
                t1,t2 = tex.calc_t2t(K1,1+K2)
                K1, K2 = (self.m.hs1+self.Ks[1]*(self.m.hs2-self.m.hs1))/self.m.s.h, (self.m.hp1+self.Ks[1]*(self.m.hp2-self.m.hp1))/self.m.s.h
                t1b,t2b = tex.calc_t2t(K1,1+K2)
        if tex != None:
            s1,s2 = tex.calc_t2s(self.Ks[0],self.Ks[1])
            if t1b!=None: quad.def_Texture(s1,t1,self.w1, s2,t2b,self.w2, tex, s1,t2,self.w1, s2,t1b,self.w2)
            else: quad.def_Texture(s1,tex.t1,self.w1, s2,tex.t2,self.w2, tex)
        self.quads.append(quad)
    def ajout_Plafond(self, plafond, ap=None, sous_plafond=False):
        if sous_plafond: y1,y2 = self.ys1,self.ys2
        else: y1,y2 = self.yp1,self.yp2
        x1, x2 = self.x1, self.x2
        w1, w2 = self.w1, self.w2
        k1 = -(E.DY_RES-y1)/E.DY_RES
        k2 = -(E.DY_RES-y2)/E.DY_RES
        if (y1>E.Y_RES): # on coupe le trapèze pour les plafonds
            r, y1 = (E.Y_RES-y1)/(y2-y1), E.Y_RES
            x1 += (x2-x1)*r
            w1 += (w2-w1)*r
        if (y2>E.Y_RES): # on coupe le trapèze pour les plafonds
            r, y2 = (y2-E.Y_RES)/(y2-y1), E.Y_RES
            x2 -= (x2-x1)*r
            w2 -= (w2-w1)*r
        if ap!=None:
            quad = Quad(x1,y1,E.Y_RES,x2,y2,E.Y_RES)
            s1 = -(self.j.a-ap.a0)/(2*pi) -0.5 + x1/E.X_RES * ap.f
            s2 = -(self.j.a-ap.a0)/(2*pi) -0.5 + x2/E.X_RES * ap.f
            quad.def_Texture(s1,y1/E.Y_RES,1, s2,1,1, ap.texture, t4=y2/E.Y_RES,w4=1)
        else:
            Zs = ((E.Y_RES-y1)*E.R2,0,0,(E.Y_RES-y2)*E.R2)
            quad = Quad(x1,y1,E.Y_RES,x2,y2,E.Y_RES,plafond.c,plafond.lum,Zs,True)
            if (plafond.tex != None):
                if plafond.incliné:
                    pv, ps = self.j.calc_PV(plafond.mur0.u), self.j.calc_PS(plafond.mur0.u)
                    if plafond.mur0.retourné or plafond.mur0.normal: pv,ps = -pv,-ps
                    if y1==E.Y_RES: w0g = w1
                    else:
                        p1 = -E.DY_RES + (-pv*E.R0 + (E.DX_RES-x1)*ps) * plafond.pente
                        k1 = 1+(E.Y_RES-y1)/p1
                        w0g = self.w1/k1
                    if y2==E.Y_RES: w0d = w2
                    else:
                        p2 = -E.DY_RES + (-pv*E.R0 + (E.DX_RES-x2)*ps) * plafond.pente
                        k2 = 1+(E.Y_RES-y2)/p2
                        w0d = self.w2/k2
                else:
                    if k1!=0: w0 = self.w1/k1
                    elif k2!=0: w0 = self.w2/k2
                    else:
                        print("k1 et k2 nuls !",end="_")
                        return
                    w0g, w0d = w0, w0                           
                if self.m.sous_secteur and not sous_plafond:
                    tex = plafond.tex.dupliquer()
                    tex.s1, tex.t1 = plafond.calc_t2Coords(self.m.x1,self.m.y1)
                    tex.s2, tex.t2 = plafond.calc_t2Coords(self.m.x2,self.m.y2)
                else: tex = self.m.texp
                K1, K2 = self.Ks[0], self.Ks[1]
                if y1==E.Y_RES and (self.z2!=self.z1):
                    z0 = E.R0/w0g
                    K1 += (K2-K1)*(z0-self.z1)/(self.z2-self.z1)
                    w1, k1, w2 = w0g, 1, self.w2
                else:
                    w1 = self.w1
                    if y2==E.Y_RES and (self.z2!=self.z1):
                        z0 = E.R0/w0d
                        K2 -= (K2-K1)*(self.z2-z0)/(self.z2-self.z1)
                        w2, k2 = w0d, 1
                    else: w2 = self.w2
                s1,s2 = tex.calc_t2s(K1,K2)
                t1,t2 = tex.calc_t2t(K1,K2)
                sJ, tJ = plafond.calc_t2Coords(self.j.x,self.j.y) # s et t de la position du joueur
                s0g, t0g = sJ+k1*(s1-sJ), tJ+k1*(t1-tJ) # s et t de bordures d'écran
                s0d, t0d = sJ+k2*(s2-sJ), tJ+k2*(t2-tJ)
                quad.def_Texture(s1,t1,w1, s0d,t0d,w0d, tex, s0g,t0g,w0g, s2,t2,w2)
        self.quads.append(quad)
    def ajout_Sol(self, sol, sous_sol=False):
        if sous_sol: y1,y2 = self.yp1,self.yp2
        else: y1,y2 = self.ys1,self.ys2
        x1, x2 = self.x1, self.x2
        w1, w2 = self.w1, self.w2
        k1 = (E.DY_RES-y1)/E.DY_RES
        k2 = (E.DY_RES-y2)/E.DY_RES
        if (y1 < 0): # on coupe le trapèze pour les sols
            r, y1 = (0-y1)/(y2-y1), 0
            x1 += (x2-x1)*r
            w1 += (w2-w1)*r
        if (y2 < 0): # on coupe le trapèze pour les sols
            r, y2 = (y2-0)/(y2-y1), 0
            x2 -= (x2-x1)*r
            w2 -= (w2-w1)*r
        Zs = (0,y1*E.R2,y2*E.R2,0)
        quad = Quad(x1,0,y1,x2,0,y2,sol.c,sol.lum,Zs,True)
        if (sol.tex != None):
            if sol.incliné: # correctif en cas de pente
                pv, ps = self.j.calc_PV(sol.mur0.u), self.j.calc_PS(sol.mur0.u)
                if sol.mur0.retourné or sol.mur0.normal: pv,ps = -pv,-ps
                if y1==0: w0g = w1
                else:
                    p1 = E.DY_RES + (-pv*E.R0 + (E.DX_RES-x1)*ps) * sol.pente
                    k1 = 1-y1/p1
                    w0g = self.w1/k1
                if y2==0: w0d = w2
                else:
                    p2 = E.DY_RES + (-pv*E.R0 + (E.DX_RES-x2)*ps) * sol.pente
                    k2 = 1-y2/p2
                    w0d = self.w2/k2
            else:
                if k1!=0: w0 = self.w1/k1
                elif k2!=0: w0 = self.w2/k2
                else:
                    print("k1 et k2 nuls !",end="_")
                    return
                w0g, w0d = w0, w0
            if self.m.sous_secteur and not sous_sol:
                tex = sol.tex.dupliquer()
                tex.s1, tex.t1 = sol.calc_t2Coords(self.m.x1,self.m.y1)
                tex.s2, tex.t2 = sol.calc_t2Coords(self.m.x2,self.m.y2)
            else: tex = self.m.texs
            K1, K2 = self.Ks[0], self.Ks[1]
            if y1==0 and (self.z2!=self.z1): # on a réduit le trapèze
                z0 = E.R0/w0g
                K1 += (K2-K1)*(z0-self.z1)/(self.z2-self.z1)
                w1, k1, w2 = w0g, 1, self.w2
            else:
                w1 = self.w1
                if y2==0 and (self.z2!=self.z1): # on a réduit le trapèze
                    z0 = E.R0/w0d
                    K2 -= (K2-K1)*(self.z2-z0)/(self.z2-self.z1)
                    w2, k2 = w0d, 1
                else: w2 = self.w2
            s1,s2 = tex.calc_t2s(K1,K2)
            t1,t2 = tex.calc_t2t(K1,K2)
            sJ, tJ = sol.calc_t2Coords(self.j.x,self.j.y) # s et t de la position du joueur
            s0g, t0g = sJ+k1*(s1-sJ), tJ+k1*(t1-tJ) # s et t de bordures d'écran
            s0d, t0d = sJ+k2*(s2-sJ), tJ+k2*(t2-tJ)
            quad.def_Texture(s0g,t0g,w0g, s2,t2,w2, tex, s1,t1,w1, s0d,t0d,w0d)
        self.quads.append(quad)
    def ajout_Fondation(self, c, lum):
        quad = Quad(t.x1,min(0,t.ys1),t.ys1,t.x2,min(0,t.ys1),t.ys1,c,lum,Zs)
        self.quads.append(quad)
    def ajout_Comble(self, c, lum):
        quad = Quad(t.x1,t.yp1,max(t.yp1,E.Y_RES),t.x2,t.yp2,max(t.yp2,E.Y_RES),c,lum,Zs)
        self.quads.append(quad)

class Quad:
    def __init__(self, x1,ys1,yp1,x2,ys2,yp2, c=None,lum=None, Zs=None,sans_bordures=False):
        self.tex = None
        self.v = [x1,ys1,0,x1,yp1,0,x2,yp2,0,x2,ys2,0]
        self.sans_bordures = sans_bordures
        self.c = c
        self.lum = lum
        self.Zs = Zs
    def def_z(self, z):
        self.v[2],self.v[5],self.v[8],self.v[11] = z,z,z,z
    def def_Texture(self, s1,t1,w1, s3,t3,w3, tex, s2=None,t2=None,w2=None, s4=None,t4=None,w4=None): # no 2 et 4 si pas trapèze
        self.tex = tex
        k = tex.échelle
        if s2==None: s2 = s1
        if s4==None: s4 = s3
        if t2==None: t2 = t3
        if t4==None: t4 = t1
        if w2==None: w2 = w1
        if w4==None: w4 = w3
        self.t4coords = [k*s1*w1,k*t1*w1,0,w1, k*s2*w2,k*t2*w2,0,w2, k*s3*w3,k*t3*w3,0,w3, k*s4*w4,k*t4*w4,0,w4]

class Lumière:
    def __init__(self, lumin, brillance, ombre, N=None):
        self.lumin = lumin
        self.brillance = brillance
        self.ombre = ombre
        self.N = N
    def ret_PS(self, v):
       return round(self.N[0]*v[0]+self.N[1]*v[1]+self.N[2]*v[2],E.NB_DECIMALES)
    def calc_Couleur(self, c, soleil=True, Zs=None):
        lumin = E.LUMIN0 + self.lumin
        if soleil: lumin_ciel = E.LUMIN_SOLEIL
        else: lumin_ciel = E.LUMIN_NUIT
        lumin += (1+self.ret_PS(E.DIR_SOLEIL))*(lumin_ciel*(1-self.ombre))/2
        dc_Plus = [round(comp*lumin*0.01) for comp in c]
        nc = tuple([max(min(c[i]+dc_Plus[i],255),0)for i in range(3)])
        # degradé
        if (E.R1 != 0) and (Zs != None):
            nc4 = tuple([round(self.modif_Intensité(nc,1-z)[comp]) for z in Zs for comp in range(3)])
        else:
            nc4 = nc*4
        return nc4
    def modif_Intensité(self, c, pourcent):
        #c = rgb_to_hls(c[0],c[1],c[2])
        #return hls_to_rgb(c[0],c[1]*pourcent,c[2])
        #c = rgb_to_hsv(c[0],c[1],c[2])
        #return hsv_to_rgb(c[0],c[1],c[2]*pourcent)
        return (min(c[0]*pourcent,255),min(c[1]*pourcent,255),min(c[2]*pourcent,255))

class Groupe0(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

class GroupeA(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan = (gl.GLdouble * 4)(1.0,0,0,-self.x)
        gl.glClipPlane(gl.GL_CLIP_PLANE0, plan)
        gl.glEnable(gl.GL_CLIP_PLANE0)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE0)

class GroupeB(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan = (gl.GLdouble * 4)(-1.0,0,0,self.x)
        gl.glClipPlane(gl.GL_CLIP_PLANE1, plan)
        gl.glEnable(gl.GL_CLIP_PLANE1)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE1)

class GroupeS(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan = (gl.GLdouble * 4)(-self.plan[0],-self.plan[1],0,-self.plan[2])
        gl.glClipPlane(gl.GL_CLIP_PLANE2, plan)
        gl.glEnable(gl.GL_CLIP_PLANE2)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE2)

class GroupeN(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan = (gl.GLdouble * 4)(self.plan[0],self.plan[1],0,self.plan[2])
        gl.glClipPlane(gl.GL_CLIP_PLANE3, plan)
        gl.glEnable(gl.GL_CLIP_PLANE3)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE3)

class GroupeAS(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan0 = (gl.GLdouble * 4)(1.0,0,0,-self.x)
        gl.glClipPlane(gl.GL_CLIP_PLANE0, plan0)
        gl.glEnable(gl.GL_CLIP_PLANE0)
        plan2 = (gl.GLdouble * 4)(-self.plan[0],-self.plan[1],0,-self.plan[2])
        gl.glClipPlane(gl.GL_CLIP_PLANE2, plan2)
        gl.glEnable(gl.GL_CLIP_PLANE2)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE0)
        gl.glDisable(gl.GL_CLIP_PLANE2)

class GroupeAN(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan0 = (gl.GLdouble * 4)(1.0,0,0,-self.x)
        gl.glClipPlane(gl.GL_CLIP_PLANE0, plan0)
        gl.glEnable(gl.GL_CLIP_PLANE0)
        plan3 = (gl.GLdouble * 4)(self.plan[0],self.plan[1],0,self.plan[2])
        gl.glClipPlane(gl.GL_CLIP_PLANE3, plan3)
        gl.glEnable(gl.GL_CLIP_PLANE3)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE0)
        gl.glDisable(gl.GL_CLIP_PLANE3)

class GroupeBS(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan1 = (gl.GLdouble * 4)(-1.0,0,0,self.x)
        gl.glClipPlane(gl.GL_CLIP_PLANE1, plan1)
        gl.glEnable(gl.GL_CLIP_PLANE1)
        plan2 = (gl.GLdouble * 4)(-self.plan[0],-self.plan[1],0,-self.plan[2])
        gl.glClipPlane(gl.GL_CLIP_PLANE2, plan2)
        gl.glEnable(gl.GL_CLIP_PLANE2)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE1)
        gl.glDisable(gl.GL_CLIP_PLANE2)

class GroupeBN(pyglet.graphics.OrderedGroup):
    def set_state(self):
        if E.MODE_DESSIN!=1:
            if self.fil: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            else: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        plan1 = (gl.GLdouble * 4)(-1.0,0,0,self.x)
        gl.glClipPlane(gl.GL_CLIP_PLANE1, plan1)
        gl.glEnable(gl.GL_CLIP_PLANE1)
        plan3 = (gl.GLdouble * 4)(self.plan[0],self.plan[1],0,self.plan[2])
        gl.glClipPlane(gl.GL_CLIP_PLANE3, plan3)
        gl.glEnable(gl.GL_CLIP_PLANE3)
    def unset_state(self):
        gl.glDisable(gl.GL_CLIP_PLANE1)
        gl.glDisable(gl.GL_CLIP_PLANE3)

