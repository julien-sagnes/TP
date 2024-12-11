from interbotix_xs_modules.arm import InterbotixManipulatorXS
import numpy as np
import sys
import time

# This script makes the end-effector perform pick, pour, and place tasks
# Note that this script may not work for every arm as it was designed for the wx250
# Make sure to adjust commanded joint positions and poses as necessary
#
# To get started, open a terminal and type 'roslaunch interbotix_xsarm_control xsarm_control.launch robot_model:=wx250'
# Then change to this directory and type 'python bartender.py  # python3 bartender.py if using ROS Noetic'
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

def capture_joint_positions(arm):
    return arm.get_joint_positions()

def main():
    bot = InterbotixManipulatorXS("px100", "arm", "gripper")
    q_all = []

    bot.arm.go_to_sleep_pose()
    bot.gripper.open()

    p = (0.15, 0.1, 0.10)
    q_all, joint_positions = MGI(p,bot.capture_joint_positions(bot))
    bot.arm.set_ee_pose_components(joint_positions)
    bot.gripper.close(delay = 1)

    bot.arm.go_to_sleep_pose()

    # bot.arm.set_ee_cartesian_trajectory(pitch=-1.5)
    # bot.arm.set_ee_pose_components(x=0.3, z=0.2)
    # bot.arm.set_single_joint_position("waist", np.pi/2.0)
    # bot.arm.set_ee_cartesian_trajectory(x=0.1, z=-0.16)
    # bot.arm.set_ee_cartesian_trajectory(x=-0.1, z=0.16)
    # bot.arm.set_single_joint_position("waist", -np.pi/2.0)
    # bot.arm.set_ee_cartesian_trajectory(pitch=1.5)
    # bot.arm.set_ee_cartesian_trajectory(pitch=-1.5)
    # bot.arm.set_single_joint_position("waist", np.pi/2.0)
    # bot.arm.set_ee_cartesian_trajectory(x=0.1, z=-0.16)
    # bot.gripper.open()
    # bot.arm.set_ee_cartesian_trajectory(x=-0.1, z=0.16)

if __name__=='__main__':
    main()
