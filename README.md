Jeu de Moulins (Nine Men's Morris)
Introduction
Le jeu de moulins, également connu sous le nom de Nine Men's Morris, est un jeu de stratégie à deux joueurs. Dans cette implémentation, le jeu se joue sur un plateau comportant 24 positions disposées en trois carrés concentriques reliés par des lignes. Les joueurs placent et déplacent des pièces pour former des "moulins" (trois pièces alignées) et bloquer leur adversaire. Cette version, basée sur les fichiers client.py, drl_env.py et server.py, simplifie certaines règles traditionnelles, notamment en omettant le retrait des pièces adverses lorsqu'un moulin est formé.
Règles du jeu
Configuration du plateau
Le plateau est composé de 24 positions où les pièces peuvent être placées. Ces positions sont connectées selon un motif spécifique, permettant aux pièces de se déplacer le long des lignes pendant la phase de déplacement. Les connexions sont définies dans le code par une liste appelée CONNECTIONS, représentant les mouvements valides entre les positions.
Phases du jeu
Le jeu est divisé en deux phases principales :

Phase de placement :

Chaque joueur commence avec 9 pièces.
Les joueurs placent à tour de rôle une pièce sur une position vide du plateau.
L'objectif est de positionner les pièces stratégiquement pour former des moulins ou préparer la phase suivante.


Phase de déplacement :

Une fois que toutes les pièces ont été placées (c'est-à-dire que les deux joueurs ont posé leurs 9 pièces), le jeu passe à la phase de déplacement.
Les joueurs déplacent à tour de rôle une de leurs pièces vers une position vide adjacente, selon les connexions définies.
L'objectif est de former des moulins ou de bloquer les mouvements de l'adversaire.



Formation d'un moulin

Un moulin est formé lorsqu'un joueur aligne trois de ses pièces sur une ligne droite le long des lignes du plateau, comme défini dans la liste mills du code.
Dans cette implémentation, lorsqu'un moulin est formé, le jeu le détecte et affiche un message (par exemple, "Joueur X a formé un moulin !"). Cependant, contrairement aux règles traditionnelles, aucune pièce adverse n'est retirée.

Conditions de victoire

Le jeu se termine lorsqu'un joueur ne peut plus effectuer de mouvement légal, c'est-à-dire lorsque toutes ses pièces sont bloquées et qu'aucune position vide adjacente n'est disponible. L'autre joueur est alors déclaré vainqueur.
Une condition de victoire alternative existe dans le code : un joueur perd s'il a moins de 3 pièces sur le plateau. Cependant, comme les pièces ne sont pas retirées dans cette implémentation, cette condition est peu susceptible de se produire.

Comparaison avec les règles traditionnelles
Dans le jeu traditionnel de Nine Men's Morris, lorsqu'un joueur forme un moulin, il peut retirer une pièce adverse du plateau, à condition que cette pièce ne fasse pas partie d'un autre moulin. Cela permet de réduire le nombre de pièces de l'adversaire, facilitant une victoire en le réduisant à moins de 3 pièces ou en bloquant ses mouvements. Dans cette implémentation, l'absence de retrait de pièces simplifie le jeu, rendant la victoire principalement dépendante du blocage des mouvements adverses.
Détails de l'implémentation
L'implémentation utilise une architecture client-serveur avec les composants suivants :



Fichier
Rôle



server.py
Gère l'état du jeu, valide les actions des joueurs et synchronise les clients via des sockets TCP.


client.py
Fournit une interface graphique avec Pygame, permettant à un joueur humain (Joueur 1) de cliquer pour placer ou déplacer des pièces, et à une IA (Joueur 2) de jouer automatiquement.


drl_env.py
Définit un environnement d'apprentissage par renforcement basé sur Gymnasium, utilisé pour entraîner une IA avec l'algorithme PPO (Proximal Policy Optimization).


server.py

Utilise la bibliothèque socket pour créer un serveur TCP sur localhost:12345, acceptant deux clients.
Maintient l'état du jeu, y compris le plateau (un dictionnaire de 24 positions), le nombre de pièces restantes à placer (pieces), la phase du jeu, et le tour du joueur.
Valide les actions des joueurs (placement ou déplacement) et vérifie les moulins après chaque action à l'aide de la fonction check_mill.
Diffuse les mises à jour de l'état du jeu aux clients en JSON.

client.py

Utilise Pygame pour afficher le plateau et gérer les interactions des joueurs.
Pour le Joueur 1 (humain), les clics de souris sont traduits en actions (placement ou déplacement) envoyées au serveur.
Pour le Joueur 2 (IA), un modèle PPO pré-entraîné (chargé depuis ppo_ninemensmorris) prédit les actions en fonction de l'état du jeu.
Reçoit les mises à jour du serveur pour synchroniser l'affichage du plateau.

drl_env.py

Implémente un environnement Gymnasium pour Nine Men's Morris, avec un espace d'observation (24 positions, 3 états possibles) et un espace d'action (576 actions possibles, représentant les placements ou déplacements).
Récompense l'agent IA avec +1 pour la formation d'un moulin, 0 sinon, et -1 pour les actions invalides.
Entraîne un modèle PPO pour apprendre à jouer en maximisant les récompenses.

Comment jouer

Démarrer le serveur :

Exécutez server.py pour lancer le serveur de jeu.


Connecter les clients :

Exécutez client.py pour lancer un client. Le premier client sera le Joueur 1 (humain), et le second sera le Joueur 2 (IA).


Jouer au jeu :

Phase de placement : Cliquez sur une position vide pour placer une pièce.
Phase de déplacement : Cliquez sur une de vos pièces, puis sur une position vide adjacente pour la déplacer.
Le jeu détecte automatiquement les moulins et affiche un message.
Le jeu se termine lorsqu'un joueur ne peut plus bouger, et le vainqueur est annoncé.



Entraînement de l'IA
L'agent IA est entraîné à l'aide de l'algorithme PPO de Stable Baselines3 dans drl_env.py. L'environnement du jeu est défini pour permettre à l'agent d'apprendre en interagissant avec le plateau, en prenant des actions (placement ou déplacement) et en recevant des récompenses (par exemple, +1 pour un moulin). Le modèle entraîné est sauvegardé sous ppo_ninemensmorris et utilisé par le client pour le Joueur 2.

Remarque
Cette implémentation diffère du jeu traditionnel de Nine Men's Morris par l'absence de retrait des pièces adverses lorsqu'un moulin est formé. Cela simplifie la stratégie, mettant l'accent sur le blocage des mouvements adverses plutôt que sur la réduction du nombre de pièces. Pour plus d'informations sur les règles traditionnelles, consultez Nine Men's Morris sur Wikipédia.
