#les patients sont repérés par leurs coordonnées dans un graphe
#les trajets sont sous forme de liste

import random as rd
import matplotlib.pyplot as plt
import pickle
import pygame


class Patient:

    def __init__(self, x, y, priorite): 
        self.x = x
        self.y = y  #coordonnées du point
        self.priorite = priorite

    def distance(self, patient):   #distance entre deux patients
        return ((patient.x - self.x)**2 + (patient.y - self.y)**2)**0.5

    def nouveauPatient(prioritaire):
        '''prioritaire = true si le patient est prioritaire, false sinon'''
        x = rd.uniform(0, x_max)
        y = rd.uniform(0, y_max)
        return Patient(x, y, prioritaire)

    def couleur(self):
        if self.priorite:
            return (255, 0, 0)
        return (0, 0, 255)

    def affichagepy(self, screen):
        pygame.draw.circle(screen, self.couleur(), (self.x *60 + 50, self.y *60 + 50), 10)
    


class ListePatient:

    def __init__(self, listePatient, nb_prioritaire):
        self.liste = listePatient
        self.nb_prioritaire = nb_prioritaire
    
    def nb_patient(self):
        return len(self.liste) - 1

    def generateurPatient(nb_patient, nb_prioritaire):
        point_de_depart = Patient(x_depart, y_depart, False) #par défaut
        liste = [point_de_depart]
        for i in range(nb_prioritaire):
            liste.append(Patient.nouveauPatient(True))
        for i in range(nb_patient - nb_prioritaire):
            liste.append(Patient.nouveauPatient(False))
        return ListePatient(liste, nb_prioritaire)
    
    def affichage(self):
        X = [self.liste[i].x for i in range(self.nb_patient()+1)]
        Y = [self.liste[i].y for i in range(self.nb_patient()+1)]
        plt.scatter(X[1:self.nb_prioritaire+1], Y[1:self.nb_prioritaire+1], c='red')
        plt.scatter(X[self.nb_prioritaire+1:], Y[self.nb_prioritaire+1:], c='blue')
        plt.scatter(X[0], Y[0], c='green')
        plt.show()


class Circuit:

    def __init__(self, trajet, distance, nb_prioritaire):
        self.trajet = trajet.copy()
        self.distance = distance
        self.nb_prioritaire = nb_prioritaire
    
    def nb_patient(self):
        return len(self.trajet) - 1

    def distance(trajet):
        dist = 0
        for i in range(len(trajet)-1) :
            dist += Patient.distance(trajet[i], trajet[i+1])
        return dist

    def nouveauCircuit(listePatient):
        trajetPrioritaire = listePatient.liste[1:(listePatient.nb_prioritaire+1)]
        trajetPatient = listePatient.liste[(listePatient.nb_prioritaire+1):]
        #rd.shuffle(trajetPrioritaire)
        rd.shuffle(trajetPatient)
        trajet = [listePatient.liste[0]] + trajetPrioritaire + trajetPatient
        circuit = Circuit(trajet, Circuit.distance(trajet), listePatient.nb_prioritaire)
        #le premier point est le point de départ, puis on ajoute la liste des patients mélangée aléatoirement
        return circuit

    def affichage(self):
        X = [self.trajet[i].x for i in range(self.nb_patient()+1)]
        Y = [self.trajet[i].y for i in range(self.nb_patient()+1)]
        plt.scatter(X[1:self.nb_prioritaire+1], Y[1:self.nb_prioritaire+1], c='red')
        plt.scatter(X[self.nb_prioritaire+1:], Y[self.nb_prioritaire+1:], c='blue')
        plt.scatter(X[0], Y[0], c='green')
        plt.plot(X, Y, 'grey')

    def generateurCircuit(listePatient, demographie):
        listeCircuit = []
        for i in range(demographie) :
            listeCircuit.append(Circuit.nouveauCircuit(listePatient))
        return listeCircuit
    
    def affichagepy(self, screen):
        listePoints = [(60*patient.x + 50, 60*patient.y + 50) for patient in self.trajet]
        pygame.draw.lines(screen, (125, 125, 125), False, listePoints)


class Population:

    def __init__(self, listeCircuit):
        self.listeCircuit = listeCircuit
        self.tauxMutation = 0.015
        self.tailleTournoi = 5

    def getElite(self) :
        '''renvoie le meilleur circuit (celui de distance la plus faible) 
        de la population'''
        meilleur_circuit = (self.listeCircuit)[0]

        for i in range(1, len(self.listeCircuit)):
            if ((self.listeCircuit)[i]).distance < meilleur_circuit.distance :
                meilleur_circuit = (self.listeCircuit)[i]

        return meilleur_circuit

    def selectionTournoi(self):
        '''renvoie le circuit avec la plus faible distance dans une poule 
        de self.tailleTournoi circuits pris au hasard dans la population'''
        meilleur_circuit = rd.choice(self.listeCircuit)
        for i in range(self.tailleTournoi - 1):
            circuit = rd.choice(self.listeCircuit)
            if circuit.distance < meilleur_circuit.distance :
                meilleur_circuit = circuit
        return meilleur_circuit

    def croisement(self, parent1, parent2):
        #Le point de départ est commun à tous les circuits, donc l'indice 
        #du début du croisement est supérieur à 1.
        debut = rd.randint(parent1.nb_prioritaire+1, parent1.nb_patient())

        fin = rd.randint(debut+1, parent1.nb_patient()+1)

        embryonT = parent1.trajet[:debut] + parent1.trajet[fin:]
        enfantT = parent1.trajet[:debut]

        for patient in parent2.trajet :
            if patient not in embryonT :
                enfantT.append(patient)
        enfantT += parent1.trajet[fin:]

        enfant = Circuit(enfantT, Circuit.distance(enfantT), parent1.nb_prioritaire)
        return enfant

    def mutation(self, circuit):
        '''échange de deux points dans un circuit avec une probabilité de self.tauxMutation'''
        if rd.random() < self.tauxMutation :
            indice_mut = rd.randint(circuit.nb_prioritaire+1, len(circuit.trajet) - 2) #On ne change pas le point de départ

            circuit.trajet[indice_mut], circuit.trajet[indice_mut+1] = circuit.trajet[indice_mut+1], circuit.trajet[indice_mut]
            circuit.distance = Circuit.distance(circuit.trajet)
        return circuit




def evolutionPopulation(listePatient, demographie = 1000, nb_generation = 40):

    if len(listePatient.liste) <= 1 :
        return Circuit(listePatient.liste, 0, listePatient.nb_prioritaire)

    if listePatient.nb_patient() - listePatient.nb_prioritaire == 1 :
        return Circuit(listePatient.liste, Circuit.distance(listePatient.liste), listePatient.nb_prioritaire)


    listeCircuit = Circuit.generateurCircuit(listePatient, demographie)
    population = Population(listeCircuit)

    meilleurCircuit = Population.getElite(population)
    DistanceMeilleurCircuit = [meilleurCircuit.distance]

    for i in range(nb_generation):
        nouveauxCircuits = [meilleurCircuit]

        for k in range(demographie - 1):
            parent1 = Population.selectionTournoi(population)
            parent2 = Population.selectionTournoi(population)

            enfant = Population.croisement(population, parent1, parent2)

            enfant = Population.mutation(population, enfant)

            nouveauxCircuits.append(enfant)

        population = Population(nouveauxCircuits)

        meilleurCircuit = Population.getElite(population)
        DistanceMeilleurCircuit.append(meilleurCircuit.distance)

    #for i in range(nb_prioritaire):
        #print(meilleurCircuit.trajet[i+1].priorite)


    #plt.figure(1)
    #On trace la distance du meilleur circuit en fonction de la génération
    #X = [i for i in range(nb_generation + 1)]
    #plt.plot(X, DistanceMeilleurCircuit)


    #plt.figure(2)
    #On trace le meilleur circuit obtenu à l'issue de toutes les générations
    #Circuit.affichage(meilleurCircuit)

    #plt.show()

    return meilleurCircuit




def affichage(screen) :
    global nb_medecin
    for i in range(nb_medecin):
        for patient in P[i].liste :
            patient.affichagepy(screen)
        if len(C[i].trajet) > 1 :
            C[i].affichagepy(screen)
        screen.blit(medecinIMG, (60 * Med[i].x + 50 - 20, 60 * Med[i].y + 50 - 20))



def nouvelle_consultation(dt):
    #Les nouvelles consultations sont forcément des urgences
    global nb_medecin
    global indic_arret
    global urgence

    if rd.random() < dt*proba_nouvelle_consultation :
        patient = Patient.nouveauPatient(True)
        indice_med = split_patient(patient, nb_medecin - urgence, urgence)
        
        #Si une urgence apparait avant le départ du médecin du point de départ, on insère l'urgence après le point de départ (résolution d'un bug)
        if P[indice_med].liste[0].x == 5 and P[indice_med].liste[0].y == 5 :
            P[indice_med].liste.insert(1, patient)
        
        else :
            P[indice_med].liste.insert(P[indice_med].nb_prioritaire +1, patient)
        
        P[indice_med].nb_prioritaire += 1
        C[indice_med].nb_prioritaire += 1
        
        #Si le médecin est urgentiste, ou si tous les patients sont prioritaires, on ajoute le patient à la suite des autres urgences
        if urgence == 1 or P[indice_med].nb_patient() == P[indice_med].nb_prioritaire :
            C[indice_med].trajet.append(patient)

        #Sinon, on calcule de nouveau le circuit
        else :
            indic_calcul_circuit[indice_med] = True
        
        indic_arret[indice_med] = False

        temps_urgence[patient] = 0




def update(dt) :
    global timer
    global journee
    global C
    global P
    global nb_medecin

    for i in range(nb_medecin) :
        if indic_arret[i] :
            continue

        if len(C[i].trajet) == 1 and indic_calcul_circuit[i] :
            C[i] = evolutionPopulation(P[i])
            indic_calcul_circuit[i] = False

        if Med[i].distance(C[i].trajet[1])<0.1 :
            if len(P[i].liste) == 2 :
                indic_arret[i] = True
                continue
            patient_precedent = C[i].trajet.pop(0)  #On enlève le patient duquel le médecin est parti
            #P[i].liste.remove(patient_precedent)
            for j in range(len(P[i].liste)):
                patient = P[i].liste[j]
                if patient == patient_precedent:
                    P[i].liste.pop(j)
                    break
            if C[i].trajet[0].priorite :
                P[i].nb_prioritaire -= 1 #On actualise le nombre de prioritaires (si le patient chez lequel le médecin arrive devient le point de départ, il n'est donc pas prioritaire)
                C[i].nb_prioritaire -= 1

            P[i].liste.remove(C[i].trajet[0]) 
            P[i].liste.insert(0, C[i].trajet[0])  #On place le patient chez lequel on arrive comme point de départ
        
            if indic_calcul_circuit[i] :
                C[i] = evolutionPopulation(P[i])
                indic_calcul_circuit[i] = False
        
            timer[i] = temps_consultation
    

    
    for i in range(nb_medecin):
        if timer[i] > 0 :
            timer[i] -= dt
        elif not indic_arret[i] :
            tempsMed[i] += dt

            norme_vect_dir = Med[i].distance(C[i].trajet[1])
            vect_normalise = ((C[i].trajet[1].x - Med[i].x)/norme_vect_dir, (C[i].trajet[1].y - Med[i].y)/norme_vect_dir)
            vect_vitesse = (vect_normalise[0]*dt*vitesse, vect_normalise[1]*dt*vitesse)

            Med[i].x += vect_vitesse[0]/60
            Med[i].y += vect_vitesse[1]/60

            if urgence == 0 :
                for patient in P[i].liste :
                    if patient.priorite :    
                        temps_urgence[patient] += dt
    
    if urgence == 1 and not indic_arret[nb_medecin - 1] :
        for patient in P[nb_medecin-1].liste[1:] :
            temps_urgence[patient] += dt
        #On ajoute dt au temps de traitement de tous les patients non encore vus
    

    journee -= dt
    if journee <= 0 :
        return
    
    nouvelle_consultation(dt)




def split_listePatient(Pinit):
    global nb_medecin
    global urgence
    #Ne fonctionne que pour nb_medecin = 2, 3, 4
    liste = [[Pinit.liste[0]] for i in range(nb_medecin)]
    #Le point de départ est commun à tous les médecins
    nb_prioritaire = [0 for i in range(nb_medecin)]
    #Initialisation
    
    for patient in Pinit.liste[1:] :
        indice_med = split_patient(patient, nb_medecin - urgence, urgence)
        liste[indice_med].append(patient)
        if patient.priorite :
            nb_prioritaire[indice_med] += 1

    P = []
    for i in range(nb_medecin):
        P.append(ListePatient(liste[i], nb_prioritaire[i]))
    
    return P


def split_patient(patient, nb_medecin, urgence) :
    if urgence == 1 :
        if patient.priorite :
            return nb_medecin
            #On met le médecin assigné aux urgences après les autres médecins dans la liste de médecins
    indice_med = 0
    if nb_medecin % 2 == 0 :
        if patient.x < 5 :
            indice_med = 0
        else :
            indice_med = 1
        #Si le nombre de médecins est divisible par 2, on divise d'abord la zone en 2

    if nb_medecin == 4 :
        if patient.y < 5 :
            indice_med = 2*indice_med
        else :
            indice_med = 2*indice_med + 1
        #Si le nombre de médecins vaut 4, on divise de nouveau les zones en 2
                 
    if nb_medecin == 3 :
        if patient.x < 3.33 :
            indice_med = 0
        elif patient.x < 6.66 :
            indice_med = 1
        else :
            indice_med = 2
        
    return indice_med





##Initialisation

x_max = 10 #le secteur couvert
y_max = 10

x_depart = 5 #point de départ du médecin
y_depart = 5


#On charge leur image
medecinIMG = pygame.image.load('medecin.png')
medecinIMG = pygame.transform.scale(medecinIMG, (40,40))

#Listes de patients initiales utilisées
MED2 = [pickle.load(open('2med_l1', 'rb')), pickle.load(open('2med_l2', 'rb')), pickle.load(open('2med_l3', 'rb')), pickle.load(open('2med_l4', 'rb'))]

MED3 = [pickle.load(open('3med_l1', 'rb')), pickle.load(open('3med_l2', 'rb')), pickle.load(open('3med_l3', 'rb')), pickle.load(open('3med_l4', 'rb'))]

MED4 = [pickle.load(open('4med_l1', 'rb')), pickle.load(open('4med_l2', 'rb')), pickle.load(open('4med_l3', 'rb')), pickle.load(open('4med_l4', 'rb'))]

MED = [MED2, MED3, MED4]



##Données

proba_nouvelle_consultation = 0.0002

journee = 72000 #12h

temps_consultation = 3000 #30 min

vitesse = 0.1

dt = 10



##Mesures

def temps_urgence_min_max_moy(temps_urgence):
    min = 144000 #durée d'une journée multipliée par 2
    max = 0
    somme = 0
    for temps in temps_urgence.values() :
        if temps < min :
            min = temps
        if temps > max :
            max = temps
        somme += temps
    moy = somme/len(temps_urgence.values())
    return min, max, moy




#Variables
nb_medecin = 2
nb_test = 1


TM = []
TU_min_max_moy = []

for j in range(2) :
    urgence = j

    #2 méthodes
    TM0 = []
    #temps de trajet de chaque médecin avec la méthode j
    TU_min_max_moy0 = [[], [], []]
    #temps de traitement de chaque urgence avec avec la méthode j

    for i in range(nb_test) :

        #On souhaite que les consultations qui apparaissent soient les mêmes lors de la comparaison des deux méthodes pour une même liste de patients. 
        #Pour cela, on "fixe l'aléatoire"
        rd.seed(3)


        #On définit une durée maximale de la journée, ici on a choisi 10h (en oubliant la pause déjeuner)
        journee = 60000


        #On replace les médecins au point de départ
        Med = [Patient(5, 5, False) for i in range(nb_medecin)]


        #Permet de ne pas recalculer le circuit à chaque itération, mais seulement lorsqu'une nouvelle consultation est ajoutée 
        indic_calcul_circuit = [False for i in range(nb_medecin)]   

        #Lorsque le médecin arrive près d'un patient, on associe à timer une valeur (ici on a choisi 2000ms ce qui correspond à 20 minutes)
        timer = [0 for i in range(nb_medecin)]

        #Utile lorsqu'il il n'y a plus de patient à voir
        indic_arret = [False for i in range(nb_medecin)]

        #Pour mesurer le temps de trajet de chaque médecin
        tempsMed = [0 for i in range(nb_medecin)]



        #On définit la liste de patient initiale
        Pinitial = MED[nb_medecin - 2][i]

        #On définit la liste de patient initiale par médecin
        P = split_listePatient(Pinitial)

        #On calcule le circuit initial pour chaque médecin
        C = []

        for i in range(nb_medecin-1):
            C.append(evolutionPopulation(P[i]))

        if urgence == 0 :
            C.append(evolutionPopulation(P[nb_medecin-1]))

        #Il y a toujours une seule urgence initialement
        else :
            C.append(Circuit(P[nb_medecin-1].liste, Circuit.distance(P[nb_medecin-1].liste), P[nb_medecin-1].nb_prioritaire))


        #Pour calculer le temps moyen de traitement d'une urgence, on calcule le temps de traitement de chaque urgence.
        #Pour cela, on crée un dictionnaire.
        #Les nouvelles urgences sont ajoutées à la liste et initialisées à 0.
        temps_urgence = {}

        if urgence == 1 :
            for patient in P[nb_medecin-1].liste[1:] :
                temps_urgence[patient] = 0

        elif urgence == 0 :
            for i in range(nb_medecin) :
                for patient in P[i].liste[1:] :
                    if patient.priorite :
                        temps_urgence[patient] = 0



        pygame.init()
        screen = pygame.display.set_mode([700, 700])
        running = True
        indic_run = True

        while journee >= 0 or indic_run :
            for event in pygame.event.get() :
                if event.type == pygame.QUIT :
                    running = False
    
            screen.fill((255, 255, 255))

            update(dt)
            affichage(screen)

            pygame.display.flip()

            indic_run = (sum(indic_arret) < nb_medecin)
            #Si tous les médecins sont à l'arrêt, indic_run = False
            #Sinon, indic_run = True

        pygame.quit()

        TM0.append(tempsMed)
        
        min, max, moy = temps_urgence_min_max_moy(temps_urgence)
        TU_min_max_moy0[0].append(min)
        TU_min_max_moy0[1].append(max)
        TU_min_max_moy0[2].append(moy)

        temps_urgence = {}
        #On remet le dictionnaire à 0
    
    TM.append(TM0)
    TU_min_max_moy.append(TU_min_max_moy0)

print(TM, TU_min_max_moy)

#On obtient deux listes :
###TM[0] contient le temps de trajet de chaque médecin pour tous les tests effectués avec la méthode 1
#  TM[1] de même avec la méthode 2
###TU_min_max_moy[0][0] contient le temps minimum de traitement d'une urgence avec la première méthode
#  TU_min_max_moy[0][1] donne le maximum, etc
#  TU[1][0, 1 ou 2] donne les mêmes informations pour la seconde méthode

