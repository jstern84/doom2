from copy import deepcopy

class X_zBuffer:
    def __init__(self, taille, Y_zBuffer=None):
        self.taille = taille
        self.Y_zBuffer = Y_zBuffer
        self.mà0()
        self.debug = False
    def mà0(self):
        self.panneaux = [[-10,-1],[self.taille,self.taille+10]]
    def màj(self, x1, x2, portail=False):
        i = 0
        panneaux = deepcopy(self.panneaux)
        for p in panneaux:
            if self.debug: print(panneaux,x1,x2,i,self.panneaux,portail)
            if x1 < p[0]:
                if x2 < p[0]:
                    if portail: self.panneaux = panneaux
                    else: self.panneaux.insert(i, [x1,x2]) # on ajoute panneau
                    return True
                else:
                    self.panneaux[i][0] = x1 # on agrandit le panneau existant
                    if x2 <= p[1]:
                        if portail: self.panneaux = panneaux
                        return True
                    del self.panneaux[i]
            elif x1 <= p[1]:
                if x2 <= p[1]:
                    if portail:
                        self.panneaux = panneaux
                    return False
                else:
                    x1 = p[0]
                    del self.panneaux[i]
            else:
                i += 1

class Y_zBuffer:
    def __init__(self, taille, hauteur, X_zBuffer=None):
        self.taille = taille
        self.hauteur = hauteur
        self.X_zBuffer =X_zBuffer
        self.mà0()
    def mà0(self):
        self.rideaux = [[-1,self.taille+1,-1,self.hauteur+1]]#,[self.taille,self.taille+10,self.hauteur,0]]
    def màj(self, x1, x2, ys=0, yp=0, ys2=0, yp2=0, fenêtre=True): # n°2 pour le return et la fenêtre intérieure au polygone
        i = 0
        bas, haut = (False,False), (False, False)
        rideaux = deepcopy(self.rideaux)
        for r in rideaux:
            R = self.rideaux[i]
            if x1 < r[0]: # nouveau(x) rideau(x) => mise à jour : bas/haut à True
                if x2 < r[0]: # nouveau rideau et c'est fini
                    if fenêtre:
                        self.rideaux.insert(i, [x1,x2,ys,yp])
                        return self.fusionner((bas[0] or ys2>=0,bas[1] or yp>=0),(haut[0] or ys<=self.hauteur,haut[1] or yp2<=self.hauteur))
                    self.rideaux = rideaux
                    return (bas[0] or ys2>=0,bas[1] or yp>=0),(haut[0] or ys<=self.hauteur,haut[1] or yp2<=self.hauteur)
                else: # on empiète sur le rideau de droite : nouveaux rideaux ...
                    if x2 > r[1]: # on l'englobe : on coupe pour l'instant
                        continuer = True
                        X2, x2 = x2, r[1]
                    else: continuer = False
                    if ys==r[2] and yp==r[3]: # prolongement rideau : on fusionne
                        R[0] = x1
                    elif ys>=r[2] and yp<=r[3]: # plus fermé : on coupe le nouveau à droite / on ferme à gauche
                        self.rideaux.insert(i, [x1, x2, ys, yp])
                        if continuer: del self.rideaux[i+1]
                        else:
                            i += 1
                            R[0] = x2
                    else: # pas mieux : on coupe l'ancien à gauche
                        self.rideaux.insert(i, [x1, r[0], ys, yp])
                        i += 1
                        if ys>r[2] or yp<r[3]: # reste un morceau : nouveau rideau
                            self.rideaux.insert(i, [r[0],x2,max(ys,r[2]),min(yp,r[3])])
                            if continuer: del self.rideaux[i+1]
                            else:
                                i += 1
                                R[0] = x2
                    bas, haut = (bas[0] or ys2>=0,bas[1] or yp>=0), (haut[0] or ys<=self.hauteur,haut[1] or yp2<=self.hauteur)
                    if not continuer: # c'est fini ... dans tous les cas c'est visible
                        if fenêtre: return self.fusionner(bas, haut)
                        self.rideaux = rideaux
                        return bas, haut
                    x1, x2 = r[1], X2 # ... sinon on reprend
            elif x1 <= r[1]: # empiète sur le rideau
                continuer = False
                if x2 > r[1]: # on dépasse à droite :
                    continuer = True # i faudra continuer, on coupe pour l'instant
                    X2, x2 = x2, r[1]
                    #if ys==r[2] and yp==r[3]: # prolongement rideau : on remplace l'ancien
                    #    del self.rideaux[i]
                    x2 = r[1]
                # désormais englobé ...
                if ys<=r[2] and yp>=r[3]: # pas mieux : rien de changé 
                    bas, haut = (bas[0] or ys2>r[2],bas[1] or yp>r[2]), (haut[0] or ys<r[3],haut[1] or yp2<r[3])
                    if not continuer:
                        if fenêtre: return self.fusionner(bas, haut)
                        self.rideaux = rideaux
                        return bas, haut
                else: # on coupe l'ancien des deux côtés ?
                    if x1>r[0]: # à gauche ?
                        R[1] = x1 # oui : partie gauche conservée
                        i += 1
                    else: # non : on remplace l'ancien rideau
                        del self.rideaux[i]
                    self.rideaux.insert(i, [x1,x2,max(ys,r[2]),min(yp,r[3])]) # partie nouvelle du milieu rajoutée
                    bas, haut = (bas[0] or ys2>r[2],bas[1] or yp>r[2]), (haut[0] or ys<r[3],haut[1] or yp2<r[3])
                    if not continuer: 
                        if fenêtre:
                            if x2<r[1]: # à droite ?
                                self.rideaux.insert(i+1, [x2,r[1],r[2],r[3]]) # oui : partie droite conservée
                            return self.fusionner(bas, haut)
                        self.rideaux = rideaux
                        return bas, haut
                x1, x2 = r[1], X2 # on reprend
            i += 1
        if fenêtre:
            return self.fusionner(bas, haut, rec)
        self.rideaux = rideaux
        return bas, haut

    def fusionner(self, bas=(False,False), haut=(False,False)): # fusionne en X et cloture les fenêtres
        #rideaux = deepcopy(self.rideaux)
        R = self.rideaux[0]
        if R[2] >= R[3] and (R[2],R[3])!=(self.hauteur,0): 
            R[2], R[3] = self.hauteur, 0 # on clôture les rideaux
            self.X_zBuffer.màj(R[0],R[1]) # et on ajoute les panneaux
        i = 0
        for r in self.rideaux[1:]:
            R = self.rideaux[i]
            if r[2]>=r[3] and (r[2],r[3])!=(self.hauteur,0):
                r[2], r[3] = self.hauteur, 0 # on clôture
                self.X_zBuffer.màj(r[0],r[1]) # et on ajoute les panneaux
            if (R[1]==r[0]) and (R[2]==r[2]) and (R[3]==r[3]): # on fusionne
                R[1] = r[1]
                del self.rideaux[i+1]
            else:
                i += 1
        return bas, haut

class zBuffer():
    def __init__(self, taille, hauteur):
        self.taille = taille
        self.hauteur = hauteur
        self.xBuf = X_zBuffer(taille)
        self.yBuf = Y_zBuffer(taille, hauteur, self.xBuf)
        self.xBuf.Y_zBuffer = self.yBuf
        self.mà0()
    def mà0(self):
        self.xBuf.mà0()
        self.yBuf.mà0()
    def afficher(self):
        print("X:",self.xBuf.panneaux, "Y:",self.yBuf.rideaux)