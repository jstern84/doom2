import pyglet
from pyglet import shapes
from math import cos, sin, sqrt, copysign

import env
E = env.Env()

class Joueur:
    def __init__(self, x, y, a, h, secteur, lot, ratio, env=None):
        global E
        self.debug = False
        if env != None: E = env
        NB_PLANS = 3
        self.plans = [pyglet.graphics.OrderedGroup(i) for i in range(NB_PLANS)]
        self.r = ratio
        self.x = x
        self.y = y
        self.a = a
        self.h_sol = h
        self.h_decal = 0
        self.s = secteur # secteur/sous-secteur courant
        self.u = (cos(a),sin(a))
        self.ug = (cos(a+E.DA_VISION),sin(a+E.DA_VISION))
        self.ud = (cos(a-E.DA_VISION),sin(a-E.DA_VISION))
        self.lot = lot
        self.keys={"alt": False}
        # joueur pour fenêtre 1
        self.tracer()
        # position précédente pour franchissement de murs
        self.xp = self.x
        self.yp = self.y
        self.sp = self.s
        self.deplacement = False
        self.n = 0 # pour double buffer
        # inertie
        self.vx, self.vy, self.vz = 0, 0, 0 # vitesses
    def avancer(self, pas):
        self.x += pas*cos(self.a)
        self.y += pas*sin(self.a)
        self.deplacement = True
    def décaler(self, pas):
        self.x += pas*sin(self.a)
        self.y -= pas*cos(self.a)
        self.deplacement = True
    def tourner(self, angle):
        self.a += angle
        self.u = (cos(self.a),sin(self.a))
        self.ug = (cos(self.a+E.DA_VISION),sin(self.a+E.DA_VISION))
        self.ud = (cos(self.a-E.DA_VISION),sin(self.a-E.DA_VISION))
        self.deplacement = True
    def monter(self, dh):
        E.H_JOUEUR += dh
        self.deplacement = True
    def chuter(self, dt=E.dt):
        self.h_decal += self.vz*dt
        if self.h_decal<=0:
            self.h_decal = 0
            self.vz = 0
            #self.deplacement = False
        else:
            self.vz -= E.g*dt
            self.deplacement = True
    def arrêt(self):
        self.deplacement = False
    def aller(self): # on sauvegarde positions et secteur
        self.xp, self.yp, self.sp = self.x, self.y, self.s
    def revenir(self): # ! devenu inutile avec glisser
        self.x = self.xp
        self.y = self.yp
        self.s = self.sp
    def glisser(self, u):
        PS = self.calc_PS_dep(u)
        self.x = self.xp + PS*u[0]
        self.y = self.yp + PS*u[1]
        self.s = self.sp
    def hauteur(self):
        return E.H_JOUEUR + self.h_sol + self.h_decal
    def en_chute(self):
        return self.h_decal != 0

    def tracer(self, decal=(0,0)):
        x, y = self.x+decal[0], self.y+decal[1]
        l = 100
        self.marquage = []
        self.marquage.append(shapes.Circle(self.r*x,self.r*y,self.r*5, color=E.C["blanc"], batch = self.lot, group=self.plans[1]))
        self.marquage.append(shapes.Line(self.r*x,self.r*y,self.r*x+self.r*l*self.ud[0],self.r*y+self.r*l*self.ud[1], color=E.C["vert"], batch = self.lot, group=self.plans[0]))
        self.marquage.append(shapes.Line(self.r*x,self.r*y,self.r*x+self.r*l*self.ug[0],self.r*y+self.r*l*self.ug[1], color=E.C["vert"], batch = self.lot, group=self.plans[0]))
        self.marquage.append(shapes.Line(self.r*x-self.r*l*self.u[0],self.r*y-self.r*l*self.u[1],self.r*x+self.r*l*self.u[0],self.r*y+self.r*l*self.u[1], color=E.C["rouge"], batch = self.lot, group=self.plans[0]))
        self.marquage.append(shapes.Line(self.r*x-self.r*l*self.u[1],self.r*y+self.r*l*self.u[0],self.r*x+self.r*l*self.u[1],self.r*y-self.r*l*self.u[0], color=E.C["rouge"], batch = self.lot, group=self.plans[0]))
        self.marquage.append(shapes.Line(self.r*x,self.r*y,self.r*x+self.r*10*self.u[0],self.r*y+self.r*10*self.u[1], color=E.C["blanc"], batch = self.lot, group=self.plans[2]))
        for m in self.marquage[1:-1]: m.opacity = 50

    def afficher(self):
        self.lot.draw()
    def calc_Distance(self,v):
        return round(sqrt((v[0]-self.x)**2 + (v[1]-self.y)**2))
    def calc_PS(self, v):
        return round((self.u[0]*v[0]+self.u[1]*v[1]),E.NB_DECIMALES)
    def calc_PV(self, v):
        return round(self.u[0]*v[1]-self.u[1]*v[0],E.NB_DECIMALES)
    def calc_PV_dep(self, v):
        return round((self.x-self.xp)*v[1]-(self.y-self.yp)*v[0],E.NB_DECIMALES)
    def calc_PS_dep(self, v):
        return round((self.x-self.xp)*v[0]+(self.y-self.yp)*v[1],E.NB_DECIMALES)

    def ret_u(self,da):
         return (cos(self.a+da),sin(self.a+da))
    def a_droite_PV(self, x, y):
        v1 = [self.xp-x, self.yp-y]
        v2 = [self.x-x, self.y-y]
        PV, PV2 = self.calc_PV_dep(v1), self.calc_PV_dep(v2)
        if abs(PV2) > abs(PV): return PV2
        else: return PV
    def franchissement(self, m):
        PV1 = self.a_droite_PV(m.x1,m.y1)
        PV2 = self.a_droite_PV(m.x2,m.y2)
        return (PV1<=0 and PV2>=0) or (PV1>=0 and PV2<=0)
            