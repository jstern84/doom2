import pyglet
from pyglet import shapes, window, clock, gl
from math import sqrt, cos, sin, tan, pi

import structure as C
import plans as P
import joueur as J
import monde as M
import scene3d as S
import sprites as I

import env
E = env.Env()

# mode:
r="n"#input("Mode plein écran (o/n) : ")
PLEIN_ECRAN = (r.upper()=="O")
        
r=1#input("Mode de dessin (0=fil_de_fer / 1=rempli / 2=rempli+bordures (lent) : ")
E.MODE_DESSIN = r

# joueur 2D
lot0 = pyglet.graphics.Batch()
# murs 2D
lot1 = pyglet.graphics.Batch()
# murs 3D
lot3 = pyglet.graphics.Batch()

CARTE_RATIO = 0.5
CARTE_XDECAL, CARTE_YDECAL = 20, 20
X0, Y0, S0 = 0, 0, 0
#X0, Y0, S0 = 0, 0, 1

# création des fenêtresc
fenêtre0 = pyglet.window.Window(E.X_RES,E.Y_RES,"Visuel 2D absolu",vsync=False)
fenêtre0.set_location(fenêtre0.get_location()[0]+100,20)
if PLEIN_ECRAN:
    écran = pyglet.canvas.get_display().get_screens()[0]
    print(écran)
    E.redef_Résolution(écran.width, écran.height)
    fenêtre0.set_visible(False)
    fenêtre1 = pyglet.window.Window(fullscreen=True, vsync=True)
else:
    fenêtre1 = pyglet.window.Window(E.X_RES,E.Y_RES,"Visuel 2.5D csubjectif")
    fenêtre1.set_location(fenêtre1.get_location()[0]+400,E.Y_RES//2)
fps = window.FPSDisplay(fenêtre1)
label = pyglet.text.Label("", font_name='Times New Roman', font_size=E.TAILLE_POLICE, x=0, y=0)
label2 = pyglet.text.Label("", font_name='Times New Roman', font_size=E.TAILLE_POLICE, x=0, y=E.Y_RES-20)
# création de la structure
s = C.Structure(env=E)
# création des plans
plan = P.Plans(s, env=E)
param = plan.plan2()
X0,Y0,S0 = param[0]
CARTE_XDECAL,CARTE_YDECAL,CARTE_RATIO = param[1]
murs0 = param[2]
n,m = plan.ret_Taille()
print("Nb de secteurs:",n," Nb de murs:",m)
# création du joueur
j = J.Joueur(X0*plan.r,Y0*plan.r,-E.A_DROIT,E.H_JOUEUR,S0,lot0,CARTE_RATIO)
# création du monde
monde = M.Monde(plan.S, murs0, j, lot1, env=E)
print("BSP:",monde.bsp.ret_Taille(),"noeuds - hauteur=",monde.bsp.ret_Hauteur(0))
# introduction des sprites
monde.S.I.modif_BSP(monde.bsp)
# rendu 2D de la carte
decal = (CARTE_XDECAL*plan.r,CARTE_YDECAL*plan.r)
monde.tracer_2D(CARTE_RATIO, decal)
# rendu 3D de la scène
scène = S.Scène3D(monde, env=E)


def redef_Env():
    C.redef_Env(E)
    P.redef_Env(E)
    M.redef_Env(E)
    S.redef_Env(E)
    I.redef_Env(E)

@fenêtre0.event
def on_key_press(symbol, modifiers):
    if symbol == window.key.Q: quit()
    j.keys[symbol] = True
@fenêtre0.event
def on_key_release(symbol, modifiers):
    try:
        del j.keys[symbol]
    except:
        pass
@fenêtre1.event
def on_key_press(symbol, modifiers):
    global label
    if symbol == window.key.Q: quit()
    j.keys[symbol] = True
    if symbol == window.key.SPACE: # interrupteur lumière
        monde.allumer(j.s)
        if j.s in plan.cieux:
            E.SOLEIL = not E.SOLEIL
            redef_Env()
            monde.init_Eclairage()
        j.deplacement=True
        afficher()
    if symbol == window.key.ENTER:
        scène.zBuf.afficher()

@fenêtre1.event
def on_key_release(symbol, modifiers):
    try:
        del j.keys[symbol]
    except:
        pass

@fenêtre0.event
def on_draw():
    fenêtre0.clear()
    j.afficher()
    monde.aff_2D()
@fenêtre1.event
def on_draw():
    pyglet.gl.glEnable(gl.GL_DEPTH_TEST)
    if not j.deplacement:
        fenêtre1.clear()
        scène.aff_3D()
    pyglet.gl.glDisable(gl.GL_DEPTH_TEST)
    pyglet.gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    fps.draw()
    label.draw()
    label2.draw()

def afficher():
    fenêtre0.switch_to()
    decal = (CARTE_XDECAL*plan.r,CARTE_YDECAL*plan.r)
    j.tracer(decal)
    fenêtre1.switch_to()
    while j.deplacement:
        try:
            scène.calc_Scène3D()
            break
        except S.recalc_3D:
            if E.DEBUG>E.DEBUG_0: print("# exception (recalc_3D) #",end=" ")
    n,m = scène.tracer_3D()
    j.deplacement = False
    label.text = "s="+str(j.s)+" calc="+scène.stats()+" quads="+str(n)+"(no="+str(m)+")(z="+str(round(scène.T.z,3))+") "
    s = monde.secteurs[j.s]
    if s.allumé == 0: label2.text = "SECTEUR éteint"
    else: label2.text = "SECTEUR allumé"

def aug_Lumin(dlumin):
    E.LUMIN0 += dlumin
    redef_Env()
    j.deplacement = True

def boucle(dt):
    global scale, posx, rot
    if j.deplacement: return # calc et tracer 3D en cours
    if E.TOUCHE_ACCEL in j.keys:
        coeff = E.COEFF_ACCEL
    elif E.TOUCHE_RAL in j.keys:
        coeff = E.COEFF_RAL
    else:
        coeff = 1
    j.aller() # on sauvegarde les positions
    if window.key.W in j.keys:
        j.décaler(-E.PAS*coeff)
    elif window.key.C in j.keys:
        j.décaler(E.PAS*coeff)
    if window.key.RIGHT in j.keys:
        if E.TOUCHE_STRAFE in j.keys:
            j.décaler(E.PAS*coeff)
        else:
            j.tourner(-E.A_ELEM*coeff/E.COEFF_PIVOT)

    if window.key.LEFT in j.keys:
        if E.TOUCHE_STRAFE in j.keys:
            j.décaler(-E.PAS*coeff)
        else:
            j.tourner(E.A_ELEM*coeff/E.COEFF_PIVOT)
    if window.key.UP in j.keys:
        j.avancer(E.PAS*coeff)
    if window.key.DOWN in j.keys:
        j.avancer(-E.PAS*coeff)
    if window.key.NUM_ADD in j.keys or window.key.PLUS in j.keys:
        if window.key.LCTRL in j.keys:
            aug_Lumin(1)
        else: j.monter(1)
    if window.key.NUM_SUBTRACT in j.keys or window.key.MINUS in j.keys:
        if window.key.LCTRL in j.keys:
            aug_Lumin(-1)
        else: j.monter(-1)
    if j.deplacement:
        afficher()

j.deplacement=True
afficher()
if E.DEBUG>=E.DEBUG_1: print("distance collision:",E.D_COLLISION)
if E.FPS==0: pyglet.clock.schedule(boucle)
else: pyglet.clock.schedule_interval(boucle, E.FPS)
pyglet.app.run()

