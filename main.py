import math, pygame 
from pygame.locals import *
from random import randint

class Musique: # ajoute son au jeu
    def __init__(self):
        self.musique = pygame.mixer.music.load('Haagrah.io.mp3')
    
    def jouerSon(self):
        try: pygame.mixer.music.play()
        except: pass

"""initialise pygame"""
pygame.init()
pygame.display.set_caption('Haagrah.io')
icon = pygame.image.load('Haagrah.io.png')
pygame.display.set_icon(icon)
musique = Musique()
musique.jouerSon()

fenTaille = (1000, 750)
fenetre = pygame.display.set_mode(fenTaille)
""""""

# permet de zoomer et dezoomer la map pour la rendre plus grande
class Fond:
    def __init__(self):
        img = pygame.image.load('background.png')
        self.originalImg = img
        self.zoom = 8
        self.modifierImg()

    # modifie la taille de l'img en fond afin d'ajuster le zoom
    def modifierImg(self):
        self.taille = self.originalImg.get_rect()[3]*self.zoom
        self.img = pygame.transform.scale(self.originalImg, (self.taille, self.taille))

    # dezoom logicielement la map afin de donner l'illusion d'un grande map
    def dezoom(self, joueur, ordinateurs, particules):
        self.zoom //= 2
        self.modifierImg()
        self.afficher()

        joueur.taille //= 3
        joueur.pos = [joueur.pos[0]//2, joueur.pos[1]//2]
        joueur.afficher()

        for ordi in ordinateurs:
            ordi.taille //= 3
            ordi.pos = (ordi.pos[0]//2, ordi.pos[1]//2)
            ordi.afficher()

        particules.extend(Particule() for _ in range(250))
        for prtcl in particules:
            prtcl.taille //= 3
            prtcl.afficher()

        ordinateurs.extend(Ordinateur() for _ in range(5))

    def afficher(self): fenetre.blit(self.img, (0,-125)) # ajoute un fond

class Joueur:
    def __init__(self):
        img = pygame.image.load('JP_Zadi.png')
        self.img = img
        self.taille = 100
        self.pos = [10, 10]
        self.changerTailleImg()

    # determine la taille du personnage graphiquement
    def changerTailleImg(self): self.tailleImg = pygame.transform.scale(self.img, (self.taille, self.taille))

    # genere la boite de collision du joueur
    def genereHitbox(self):
        self.hitboxTaille = (self.taille//2)*(math.cos(math.pi/4))*2    # creer la hitbox du perso
        self.hitboxPos = tuple(pos + (self.taille - self.hitboxTaille)//2 for pos in self.pos)

    # affiche la hitbox
    def afficherHitbox(self):
        pygame.draw.rect(fenetre, (20,255,20), pygame.Rect(
            ( self.hitboxPos[0], self.hitboxPos[1], self.hitboxTaille, self.hitboxTaille )
        ))

    # permet de deplacer le joueur avec des fleches
    def deplacer(self):
        touche = pygame.key.get_pressed()
        if touche[pygame.K_LEFT]: self.pos[0] -= 1
        elif touche[pygame.K_RIGHT]: self.pos[0] += 1

        if touche[pygame.K_UP]: self.pos[1] -= 1
        elif touche[pygame.K_DOWN]: self.pos[1] += 1
        self.genereHitbox()

    # permet de verifier si une entité se situe dans notre hitbox pour la manger
    def manger(self, bouffes):
        for bouffe in bouffes:
            if (self.hitboxPos[0] <= bouffe.pos[0] <= self.hitboxPos[0] + self.hitboxTaille and
                self.hitboxPos[1] <= bouffe.pos[1] <= self.hitboxPos[1] + self.hitboxTaille and
                self.taille/2 > bouffe.taille ):

                self.taille += bouffe.taille
                self.pos = [pos-bouffe.taille//2 for pos in self.pos]  # fait grandir le perso depuis son centre
                if bouffe.taille >= 50: musique.jouerSon() # joue un cri de la victoire quand on vainc une proie
                bouffes.remove(bouffe)
                self.changerTailleImg()

            else: bouffe.afficher()

    # affiche le joueur
    def afficher(self):
        self.changerTailleImg()
        self.genereHitbox()
        fenetre.blit(self.tailleImg, tuple(self.pos))

class Particule:
    def __init__(self):
        self.pos = (randint(0, fenTaille[0]), randint(0, fenTaille[1]))
        self.couleur = (255, 0, 0)
        self.taille = randint(2,10)
        self.afficher()

    # affiche les particules
    def afficher(self): pygame.draw.circle(fenetre, self.couleur, self.pos, self.taille)

class Ordinateur:
    def __init__(self):
        self.pos = (randint(20, fenTaille[0]-20), randint(20, fenTaille[0]-20))
        self.taille = 50
        self.couleur = (randint(0,255), randint(0,255), randint(0,255))
        self.cible = None
        self.afficher()

    def genereHitbox(self):
        self.hitboxTaille = (self.taille)*(math.cos(math.pi/4))*2    # creer la hitbox de l'ordi
        self.hitboxPos = tuple(pos - self.hitboxTaille//2 for pos in self.pos)

    # affiche la hitbox
    def afficherHitbox(self):
        pygame.draw.rect(fenetre, (20,255,20), pygame.Rect(
            ( self.hitboxPos[0], self.hitboxPos[1], self.hitboxTaille, self.hitboxTaille )
        ))

    # fait suivre le bot un axex vers une particule afin qu'il puisse grandir
    def deplacer(self):
        if self.cible not in particules: self.cible = particules[randint(0, len(particules)-1)]
        self.cible.couleur = self.couleur
        coord = (self.pos[0]-self.cible.pos[0], self.pos[1]-self.cible.pos[1])

        x = coord[0]//abs(coord[0]) if coord[0] != 0 else 0
        y = coord[1]//abs(coord[1]) if coord[1] != 0 else 0
        self.pos = (self.pos[0] - x, self.pos[1] - y)
        self.genereHitbox()

    # verifie si une particule est dans sa hitbox pour la manger
    def manger(self, bouffes):
        for bouffe in bouffes:
            if (self.hitboxPos[0] <= bouffe.pos[0] <= self.hitboxPos[0] + self.hitboxTaille and
                self.hitboxPos[1] <= bouffe.pos[1] <= self.hitboxPos[1] + self.hitboxTaille and
                self.taille > bouffe.taille and self != bouffe ):

                self.taille += bouffe.taille//2
                if bouffe.taille >= 50: musique.jouerSon() # joue un cri de la victoire quand on vainc une proie
                bouffes.remove(bouffe)
                self.afficher()

            else: bouffe.afficher()

    # permet de voir si il peut manger le joueur
    def mangerJoueur(self, joueur):
        if (self.hitboxPos[0] <= joueur.pos[0]+joueur.taille//2 <= self.hitboxPos[0]+self.hitboxTaille and
            self.hitboxPos[1] <= joueur.pos[1]+joueur.taille//2 <= self.hitboxPos[1]+self.hitboxTaille and
            self.taille > joueur.taille//2):

            self.taille += joueur.taille//2
            joueur.taille = 0
            musique.jouerSon()
            joueur.changerTailleImg()

        else: joueur.afficher()

    # affiche les bots
    def afficher(self):
        self.genereHitbox()
        pygame.draw.circle(fenetre, self.couleur, self.pos, self.taille)


fond = Fond()
joueur = Joueur()
particules = [Particule() for _ in range(250)]
ordinateurs = [Ordinateur() for _ in range(5)]

while True:
    fond.afficher()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP: musique.jouerSon()
        elif event.type == pygame.QUIT: pygame.quit()       # quitte la page avec la croix
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit()

    joueur.deplacer()
    joueur.manger(particules)
    joueur.manger(ordinateurs)
    joueur.afficher()
    #joueur.afficherHitbox()

    if len(particules) <= len(ordinateurs): particules.extend(Particule() for _ in range(5))

    allTaille = [joueur.taille//2]
    for ordi in ordinateurs:
        ordi.deplacer()
        ordi.afficher()
        ordi.manger(particules)
        ordi.manger(ordinateurs)
        ordi.mangerJoueur(joueur)
        #ordi.afficherHitbox()
        allTaille.append(ordi.taille)

    if max(allTaille) > fenTaille[1]/4 and fond.zoom > 1: fond.dezoom(joueur, ordinateurs, particules)

    pygame.time.delay(7)
    pygame.display.flip()