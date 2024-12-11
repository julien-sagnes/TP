# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 14:14:37 2024

@author: SAGNE
"""

import matplotlib.animation as animation
from matplotlib import pyplot as plt
import numpy as np
from math import sin, cos
import time

L1=89.45
Lr=105.95
L3=100
L4=109
Lm=35
L2=100

phi=np.arctan(100/35) #angle triangle O1-O2-O2prime

plt.rcParams["figure.figsize"] = [14, 10]
plt.rcParams["figure.autolayout"] = True
fig = plt.figure()
ax = fig.add_subplot(projection="3d")

def compute_robot_points(q):

    O0=[0,0,0] # repere 0 en rouge

    O1=[0, 0, L1] #repere 1 en rouge

    O2=[cos(q[0])*(Lr*cos(q[1])), sin(q[0])*(Lr*cos(q[1])), -Lr*sin(q[1]) +L1] #repere 2 en rouge

    O2p=[cos(q[0])*(L2*cos(q[1]-np.pi/2+phi)),  sin(q[0])*(L2*cos(q[1]-np.pi/2+phi)), - L2*sin(q[1]-np.pi/2+phi) +L1] #point O2prime sur le corps 2 en bleu

    O3=[cos(q[0])*(Lr*cos(q[1])+ L3*cos(q[1]+q[2])),  
        sin(q[0])*(Lr*cos(q[1])+ L3*cos(q[1]+q[2])), 
        - Lr*sin(q[1]) - L3*sin(q[1]+q[2])+L1] #repere 3 en rouge

    O4=[cos(q[0])*(Lr*cos(q[1])+ L3*cos(q[1]+q[2])+L4*cos(q[1]+q[2]+q[3])),  
        sin(q[0])*(Lr*cos(q[1])+ L3*cos(q[1]+q[2])+L4*cos(q[1]+q[2]+q[3])), 
        - Lr*sin(q[1]) - L3*sin(q[1]+q[2])-L4*sin(q[1]+q[2]+q[3])+L1] #repere 4 en vert
    
    x = [O0[0], O1[0], O2p[0], O2[0], O3[0], O4[0]]
    y = [O0[1], O1[1], O2p[1], O2[1], O3[1], O4[1]]
    z = [O0[2], O1[2], O2p[2], O2[2], O3[2], O4[2]]
       
    return x, y, z

if __name__=='__main__':

    qi=np.array([0,-phi,phi,0])     #config. initiale (DH) de la figure
    qf=np.array([np.pi/2,-phi,phi-np.pi/2,-np.pi/2]) #config finale (DH)

    # animation
    N=10 # Number of frame
    for i in range(N+1):
       
        q=qi+(qf-qi)*i/N

        x, y, z = compute_robot_points(q)

        ax.set_xlabel('x axis')
        ax.set_ylabel('y axis')
        ax.set_zlabel('z axis')
        ax.scatter(x, y, z, c=['red', 'red', 'blue', 'red', 'red', 'green'], s=20) #points sur les liaisons
        ax.plot(x, y, z) #tracer des lignes entres les points
        plt.pause(0.1) #pause avec duree en secondes

    plt.show()

def convertir_q_qa(q):
    """
    Parameters
    ----------
    q : vecteur de coordonnées articulaires

    Returns qa : vecteur de commande
    -------
    Convertit le vecteur q en qa
    """
    qa = q
    qa[1] = q[1] + np.arctan(L2/Lm)
    qa[2] = q[2] - np.arctan(L2/Lm)
    return qa


print()
print("=====================")
print(f"Vecteur q = {q}")

qa = convertir_q_qa(q)

print(f"Vecteur q_a = {qa}")
print()

def convertir_qa_q(qa):
    """
    Parameters
    ----------
    qa : vecteur de commande

    Returns q : vecteur de coordonnées articulaires
    -------
    Convertit le vecteur qa en q
    """
    q = qa
    q[1] = qa[1] - np.arctan(L2/Lm) 
    q[2] = qa[2] + np.arctan(L2/Lm)
    return q

print(f"On peut revenir au vecteur q = {convertir_qa_q(qa)}")
print("=====================")

def transformation_homogene(q):
    """
    Parameters
    ----------
    q : vecteur de coordonnées articulaires

    Returns T
    -------
    Renvoie la matrice de transformation homogène
    """
    q1 = q[0]
    q2 = q[1]
    q3 = q[2]
    q4 = q[3]
    #Calcul des différents composants de la matrice
    T11 = np.cos(q1) * np.cos(q2 + q3 + q4)
    T12 = - np.cos(q1) * np.sin(q2 + q3 + q4)
    T13 = - np.sin(q1)
    T14 = np.cos(q1) * (Lr*np.cos(q2) + L3*np.cos(q2 + q3) + L4*np.cos(q2 + q3 + q4))
    T21 = np.sin(q1) * np.cos(q2 + q3 + q4)
    T22 = - np.sin(q1) * np.sin(q2 + q3 + q4)
    T23 = np.cos(q1)
    T24 = np.sin(q1) * (Lr*np.cos(q2) + L3*np.cos(q2 + q3) + L4*np.cos(q2 + q3 + q4))
    T31 = - np.sin(q2 + q3 + q4)
    T32 = - np.cos(q2 + q3 + q4)
    T33 = 0
    T34 = L1 - (Lr*np.sin(q2) + L3*np.sin(q2 + q3) + L4*np.sin(q2 + q3 + q4))
    T41 = 0
    T42 = 0
    T43 = 0
    T44 = 1
    T = np.array([[T11,T12,T13,T14],
         [T21,T22,T23,T24],
         [T31,T32,T33,T34],
         [T41,T42,T43,T44]])
    
    #On rajoute la rotation entre le repère 4 et l'effecteur
    T4E = np.array([[0,0,1,0],
                    [-1,0,0,0],
                    [0,-1,0,0],
                    [0,0,0,1]])
                    
    T = np.dot(T,T4E)
    return T

T = transformation_homogene(q)

print()
print("=====================")
print(f"Matrice de transformation homogène :")
print("T = ")
print(T)
print("=====================")

print()
print("=====================")
print(f"On trouve alors le modèle géométrique suivant :")

q1 = q[0]
q2 = q[1]
q3 = q[2]
q4 = q[3]

px = T[0,3]
py = T[1,3]
pz = T[2,3]
psi = q2 + q3 + q4

p = [px,py,pz,psi]

print("px =", px)
print("py =", py)
print("pz =", pz)
print("psi =", psi)
print("=====================")

def MGI(p,q_actual):
    """
    Parameters
    ----------
    p : vecteur de coordonnées opérationnelles
    q_actual : vecteur de coordonnées articulaires acteul (avant le mouvement)

    Returns q : vecteur de coordonnées articulaires
    -------
    Renvoie le modèle géométrique inverse
    """
    px = p[0]
    py = p[1]
    pz = p[2]
    psi = p[3]
    
    #On va comparer la différences des normes entre la configuration actuelle et
    #celle à atteindre. On prend la solution la plus proche de la configuration
    #actuelle qu'on déterminera grâce au MDG
    
    q_all = np.zeros((6,4))
    
    # Initialisation des variables pour stocker les solutions
    q_all = np.full((6, 4), np.nan)
    
    # Boucle unique pour calculer les six solutions
    for i in range(6):
        # Calcul de q1 avec les décalages nécessaires
        if i < 2:
            q1 = np.arctan2(py, px)  # + 0 pour les deux premières itérations
        elif i < 4:
            q1 = np.arctan2(py, px) + np.pi  # + pi pour les deux suivantes
        else:
            q1 = np.arctan2(py, px) - np.pi  # - pi pour les deux dernières
        
        # Calcul des variables intermédiaires
        U = px * np.cos(q1) + py * np.sin(q1) - L4 * np.cos(psi)
        V = L1 - pz - L4 * np.sin(psi)
        A = 2 * Lr * U
        B = 2 * Lr * V
        W = U**2 + V**2 + Lr**2 - L3**2
        eps = -1 if i % 2 == 0 else 1  # Alternance de eps (-1 pour pair, 1 pour impair)
        
        # Vérification du racine carrée
        rc = A**2 + B**2 - W**2
        if rc < 0:
            print(f"Racine carrée négatif pour i={i} : {rc}. Impossible de calculer le MGI.")
        else:
            # Calcul des angles q2, q3 et q4
            q2 = np.arctan2(B * W - eps * A * np.sqrt(rc),
                            A * W + eps * B * np.sqrt(rc))
            q3 = np.arctan2(-U * np.sin(q2) + V * np.cos(q2),
                            U * np.cos(q2) + V * np.sin(q2) - Lr)
            q4 = psi - q2 - q3
            
            # Stockage des résultats
            q_all[i, :] = [q1, q2, q3, q4]

            
        # Initialisation pour trouver le q le plus proche
        temp_min = float('inf')  # Infini pour comparer directement
        q_opti = None

        # Recherche du q optimal
        for q_i in q_all:
            if not np.isnan(q_i).any():  # Vérifie que la solution est valide (pas de NaN)
                norm_diff = np.linalg.norm(q_i) - np.linalg.norm(q_actual)  # Différence de norme
                if norm_diff < temp_min:
                    temp_min = norm_diff
                    q_opti = q_i

        if q_opti is None:
            print("Aucune solution valide trouvée.")
    return q_all, q_opti

print()
# Impression des résultats
print("=====================")
print("Modèle géométrique inverse :")

print(" - On part d'un q initial :")
q_actual = np.array([0, 0, 0, 0])  # q_initial en tant que tableau numpy pour faciliter les calculs
print(f"q_actual = {q_actual}")
# Calcul des solutions du MGI
q_MGI,q_opti = MGI(p,q_actual)

print("Solutions MGI (q_MGI) :")
print(q_MGI)
print("")

print(" - On veut arriver à ce p :")
p = [px, py, pz, psi]
print(f"p = {p}")

print(" - Et le q optimal est :")

print(q_opti)

print("=====================")


print("")
print("=====================")
print('Jacobienne du MGI :')

def jacobienne(q):
    """
    Parameters
    ----------
    q : vecteur de coordonnées articulaires

    Returns J : la jacobienne
    -------
    Renvoie la jacobienne
    """
    q[0] = q1
    q[1] = q2
    q[2] = q3
    q[3] = q4
    
    # Calcul des dérivées exactes par rapport à q1, q2, q3, q4
    # Dérivées de px
    dpx_dq1 = -(Lr * np.cos(q2) + L3 * np.cos(q2 + q3) + L4 * np.cos(q2 + q3 + q4)) * np.sin(q1)
    dpx_dq2 = -(Lr * np.sin(q2) + L3 * np.sin(q2 + q3) + L4 * np.sin(q2 + q3 + q4)) * np.cos(q1)
    dpx_dq3 = -(L3 * np.sin(q2 + q3) + L4 * np.sin(q2 + q3 + q4)) * np.cos(q1)
    dpx_dq4 = - L4 * np.sin(q2 + q3 + q4) * np.cos(q1)
    
    # Dérivées de py
    dpy_dq1 = (Lr * np.cos(q2) + L3 * np.cos(q2 + q3) + L4 * np.cos(q2 + q3 + q4)) * np.cos(q1)
    dpy_dq2 = -(Lr * np.sin(q2) + L3 * np.sin(q2 + q3) + L4 * np.sin(q2 + q3 + q4)) * np.sin(q1)
    dpy_dq3 = -(L3 * np.sin(q2 + q3) + L4 * np.sin(q2 + q3 + q4)) * np.sin(q1)
    dpy_dq4 = - L4 * np.sin(q2 + q3 + q4) * np.sin(q1)
    
    # Dérivées de pz
    dpz_dq1 = 0  # pz ne dépend pas de q1
    dpz_dq2 = - Lr * np.cos(q2) - L3 * np.cos(q2 + q3) - L4 * np.cos(q2 + q3 + q4)
    dpz_dq3 = - L3 * np.cos(q2 + q3) - L4 * np.cos(q2 + q3 + q4)
    dpz_dq4 = - L4 * np.cos(q2 + q3 + q4)
    
    # Construire la Jacobienne
    J = np.array([[dpx_dq1, dpx_dq2, dpx_dq3, dpx_dq4],
                 [dpy_dq1, dpy_dq2, dpy_dq3, dpy_dq4],
                 [dpz_dq1, dpz_dq2, dpz_dq3, dpz_dq4]])
    
    return J

# Calculer la Jacobienne
J = jacobienne(q)
print("J =")
print(J)

print("=====================")
print("")

print("=====================")
print('Pseudo-inverse de la jacobienne :')
pseudo_inverse_J = np.linalg.pinv(J)
print("J# =")
print(pseudo_inverse_J)

print("=====================")
print("")

# type: ignore #def MCI()