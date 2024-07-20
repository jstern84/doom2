import pyglet
from pyglet import sprite

import monde

import env
E = env.Env()

def redef_Env(env):
	global E
	E = env

# catégories
ARBRES, VOITURES, POUBELLES = 1, 2, 3
IMAGES = {ARBRES:[None,('arbre.gif',(95,25),2),('arbre2.png',(0,0),1)],
				VOITURES: [None,('fiat500x.png',(260,50),0.5)],
				POUBELLES: [None,('poubelle_recyclable.png',(200,80),0.3),('poubelle_tout.png',(210,90),0.3)]}

class Sprite():
	def __init__(self, image, ancre=(0,0), position=(0,0,0), échelle=1):
		self.image = image
		self.ancre0_x, self.ancre0_y = ancre[0], ancre[1]
		self.x, self.y, self.h = position[0], position[1], position[2] # position 3D dans le plan
		self.X, self.Y = 0, 0 # positions sur l'écran
		self.échelle0 = échelle
		if type(image)==pyglet.image.Animation:
			self.largeur0, self.hauteur0 = image.get_max_width(), image.get_max_height()
		else:
			self.largeur0, self.hauteur0 = image.width, image.height
	def intro_BSP(self, bsp): # inclut le sprite dans le BSP
		m = bsp.n
		a_droite = m.a_droite(self.x, self.y) # sprite à droite ?
		if a_droite:
			if bsp.d==None: # on a atteint la feuille nouvelle
				bsp.d = [self]
			elif type(bsp.d)==list: # une feuille déjà présente
				bsp.d.append(self)
			else: # on creuse encore
				self.intro_BSP(bsp.d)
		else:
			if bsp.g==None: # on a atteint la feuille nouvelle
				bsp.g = [self]
			elif type(bsp.g)==list: # une feuille déjà présente
				bsp.g.append(self)
			else: # on creuse encore
				self.intro_BSP(bsp.g)

	def app_Echelle(self, échelle):
		self.échelle = self.échelle0 * échelle
		self.ancre_x = self.ancre0_x * self.échelle
		self.ancre_y = self.ancre0_y * self.échelle
		self.largeur = self.largeur0 * self.échelle
		self.hauteur = self.hauteur0 * self.échelle

	def init_SiVisible(self, M):
		v = [self.x-M.j.x, self.y-M.j.y]
		x, d = M.j.calc_PV(v), M.j.calc_PS(v)
		xmax = E.TAN_DA_VISION*d
		if (d > 0): # sprite dans le champ de vision ?
			hj = M.j.hauteur()
			k = 1/d
			self.app_Echelle(k*E.ECHELLE_SPRITE)
			self.X, self.Y, self.Z = -E.R0*x*k+E.DX_RES-self.ancre_x, (self.h-hj)*E.R0*k+E.DY_RES-self.ancre_y, d
			Xmin, Ymin = -self.largeur, -self.hauteur
			Xmax, Ymax = E.X_RES, E.Y_RES
			return (self.X < Xmax) and (self.X > Xmin) and (self.Y < Ymax) and (self.Y > Xmin)
		return False


class Sprites():
	def __init__(self, env=None):
		global E
		self.debug = E.DEBUG
		if env != None: E = env
		self.images = {}
		self.sprites = []
		for cat in IMAGES:
			self.images[cat] = [None]
			for i in IMAGES[cat][1:]:
				try:
					image = (pyglet.resource.animation('sprites/'+i[0]), i[1], i[2]) # fichier + ancre + échelle0
					self.images[cat].append(image)
				except pyglet.resource.ResourceNotFoundException:
					if E.DEBUG>E.DEBUG_0: print("# exception (image introuvable) #",end=" ")
	def ajout_Sprite(self, image, position, échelle=1, rotation=0):
		image = self.images[image[0]][image[1]]
		s = Sprite(image[0], image[1], position, image[2])
		self.sprites.append(s)
		if (échelle != 1) or (rotation != 0): s.sprite.update(scale=échelle, rotation=rotation)
	def modif_BSP(self, bsp):
		for s in self.sprites:
			s.intro_BSP(bsp)