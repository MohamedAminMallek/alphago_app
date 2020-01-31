# alphago_app

## Implementation des règles
Pour implémenter le jeu de go et ses règles, nous avons repris le code de Aku Kotkavuo <aku@hibana.net> (Cf. https://github.com/eagleflo/goban).
Il a implémenté une version simplifiée du jeu de Go sans les règles. C'est pourquoi nous avons rajouté 
les règles qui suivent : 
* ne pas autoriser les mouvements "suicides", sauf dans le cas où il permet une capture
* détecter la fin de la partie (deux pass ou un qui abandonne),
* autoriser le fait de passer, 
* donner le gagnant en comptant simplement les pierres de chaque adversaire.

Il manque la règle du ko, ainsi qu'une vraie fonction de scoring.



## Monte Carlo Tree Search
On a commencé par implémenter une version simplifiée du MCTS. Voici le principe de cet algorithme en image :

<img src="https://media.geeksforgeeks.org/wp-content/uploads/mcts_own.png"  width="700" height="400" />

**Sélection**: Afin d'attribuer un score à chaque noeud nous avons utilisé la fonction suivante:

<img src="https://media.geeksforgeeks.org/wp-content/uploads/CodeCogsEqn-8.png" />

> ***xi*** *la récompense en fonction des victoires et des défaites,*

> ***C*** *une constante,*

> ***t*** *le nombre de visites du noeud parent,*

> ***ni*** *le nombre de visites du noeud actuel*

**Simulation** : Pour une première implémentation, on a choisit de commencer avec des parties aléatoires.

## Utilisation d'un réseau de neuronnes
Afin de rendre plus réaliste le coup joué par l'IA au cours de la simulation, nous avons entraîné un modèle sur une base de données de 50k parties, sur un plateau de 9x9.
Nous avons obtenu une accuracy de 0.4, c'est-à-dire que 40% des coups joués par notre réseau ressemblent à ceux joués par des joueurs professionels. 
<img src="https://raw.githubusercontent.com/MohamedAminMallek/alphago_app/master/images/model.png" />

