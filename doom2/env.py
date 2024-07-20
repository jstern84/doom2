from pyglet import window
from math import pi, cos, sin, tan, sqrt

class Exceptions(Exception):
    pass

class Env():
	def __init__(self):
		self.NB_DECIMALES=5 # pas en dessous de 4 ! (problème avec les petits ratios comme les sk1 pour texture quand coupé_G ou coupé_D par ex)
		self.TAILLE_POLICE=16
		self.DEBUG_0 = 0
		self.DEBUG_1 = 1
		self.DEBUG_2 = 2
		self.DEBUG = self.DEBUG_0

		#couleurs et lumière
		self.C = {'noir':(0,0,0),'blanc':(255,255,255),'noir':(0,0,0),"vert":(0,255,0),"bleu":(0,0,255),"rouge":(255,0,0),"rose":(249, 66, 158)}
		self.C['rougef'], self.C['rougeff'] = (100,0,0), (50,0,0)
		self.C['vertf'], self.C['verff'] = (0,100,0), (0,50,0)
		self.C['bleu'], self.C['bleuf'], self.C['bleuff']=(0,0,255), (0,0,100), (0,0,50)
		self.C['gris'], self.C['grisf']=(100,100,100), (50,50,50)
		self.C['jaune'], self.C['jaunef'], self.C['jauneff']=(255,255,0), (150,150,0), (100,100,0)
		self.C['beigec'], self.C['beige'] = (245, 245, 220), (200, 173, 127)
		self.COUL_TEX = self.C['blanc']
		self.COUL_FOND = None#self.C['blanc']
		self.COEF_MOTIF = 128

		#écran
		self.PLEIN_ECRAN = False
		self.X_RES, self.Y_RES = 800,600
		self.DX_RES, self.DY_RES = self.X_RES//2,self.Y_RES//2
		self.CLOCK_INTERVAL = 1/30.
		self.ECHELLE_SPRITE = self.Y_RES/3
		self.DZ = 0.001 # delta Z pour les couches 2D dessinés

		# Mode dessin : 0=fil de fer / 1=rempli / 2=rempli+bordures
		self.MODE_DESSIN = 0
		self.AFF_SPRITES = True
		self.CLIP_A = 0
		self.CLIP_B = 1
		self.CLIP_S = 2
		self.CLIP_N = 3
		
		# moteur
		self.COLLISION = True
		self.X_ZBUFFER = True
		self.Y_ZBUFFER = True
		self.SPRITEX_ZBUFFER = True
		self.SPRITEY_ZBUFFER = True
		self.GROUPER_ETAGES = False#True
		self.FPS = 0#1/30.


		# Joueur
		self.TOUCHE_STRAFE = window.key.LALT
		self.TOUCHE_ACCEL = window.key.LSHIFT
		self.TOUCHE_RAL = window.key.LCTRL
		self.COEFF_ACCEL = 4
		self.COEFF_RAL = 0.1
		self.PAS = 4
		self.A_ELEM = pi/20
		self.COEFF_PIVOT = 4 # diviseur pour touner
		self.H_JOUEUR = 50
		self.H_SAUT = 10
		self.dt, self.g = 0.2, 9.81
		self.D_COLLISION = sqrt(2*(self.PAS*self.COEFF_ACCEL)**2)
		self.A_DROIT = pi/2
		self.A_VISION = pi/2.5
		self.DA_VISION = self.A_VISION/2
		self.COS_DA_VISION = cos(self.DA_VISION)
		self.SIN_DA_VISION = sin(self.DA_VISION)
		self.TAN_DA_VISION = tan(self.DA_VISION)
		self.R0 = self.DX_RES/tan(self.DA_VISION)
		self.Rc = self.DX_RES/sin(self.DA_VISION)
		self.COTAN_DA_VISION_Y = self.R0/self.DY_RES # nécessaire pour texture des pentess
		# lumière
		self.LUMIN0 = 0
		self.BRILLANCE = 0
		self.R1 = 1*self.R0 # distance pour I/2 (murs)
		self.R2 = 0.5/self.DY_RES # coefficient pour avoir I à l'horizon des plafonds et sols
		self.SOLEIL = False
		self.A_SOLEIL = -self.A_DROIT  # au sud
		self.H_SOLEIL = self.A_DROIT/3*2 # à mi-hauteur
		self.DIR_SOLEIL=(cos(self.H_SOLEIL)*cos(self.A_SOLEIL),cos(self.H_SOLEIL)*sin(self.A_SOLEIL),sin(self.H_SOLEIL))
		self.LUMIN_SOLEIL = 50
		self.LUMIN_NUIT = 5
		self.CIEL = -1

	def redef_ModeDessin(self, mode):
	    self.MODE_DESSIN = mode

	def redef_Résolution(self, largeur, hauteur):
	    self.X_RES, self.Y_RES = largeur, hauteur
	    self.DX_RES, self.DY_RES = self.X_RES//2, self.Y_RES//2
	    self.ECHELLE_SPRITE = self.Y_RES/3
	    self.R0 = self.DX_RES/tan(self.DA_VISION)
	    self.Rc = self.DX_RES/sin(self.DA_VISION)
	    self.R1 = 1*self.R0
	    self.R2 = 0.75/self.DY_RES


	def redef_Lumin0(self, lumin):
	    self.LUMIN0 = lumin


