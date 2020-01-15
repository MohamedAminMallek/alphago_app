"""
En bref, chaque filet a un but différent, comme vous l'avez mentionné :

Le réseau de valeurs a été utilisé au niveau des nœuds de feuilles pour réduire la profondeur de la recherche de l'arbre.
Le réseau des politiques a été utilisé pour réduire l'étendue de la recherche à partir d'un nœud (orientation vers des actions immédiates prometteuses).

En général, vous pouvez utiliser les méthodes de fonction de valeur pour trouver une politique optimale
ou rechercher directement dans l'espace des politiques pour optimiser une fonction de politique paramétrée (bien sûr, il y a des avantages et des inconvénients). 
Vous pouvez utiliser des approximateurs de fonction (p. ex. Deep Nets) dans chaque cas. 
Je vois que vous êtes principalement confus au sujet du policy net, alors je concentre ma réponse sur ce point.

Le policy net a été le premier :
formé pour faire les coups qu'un humain ferait le plus probablement étant donné un état du plateau (donc l'entrée est un état du plateau 
et la sortie est un histogramme qui montre la probabilité de chaque action étant donné cet état). 
Le réseau peut approximer la fonction de probabilité sous-jacente à la mise en correspondance des états avec les actions. 
Il est raisonnable de penser à commencer à construire votre politique à partir des données disponibles après tout. 
Après une formation supervisée avec des mouvements d'experts,
le filet de politique pourrait jouer le jeu de manière suffisante (bien que loin d'un niveau de maîtrise). 
Simplement, vous avez tenté de saisir le schéma général de sélection des actions des joueurs professionnels.

Ensuite,
il a été formé aux jeux avec l'adversaire lui-même, afin d'optimiser la politique apprise précédemment. 
Cette fois-ci, ses poids ont été mis à jour à l'aide de l'algorithme REINFORCE. 
En faisant cela, vous mettez à jour les paramètres nets vers la maximisation de la récompense attendue.
Finalement, vous avez un filet qui ne sélectionne pas seulement les actions comme un joueur professionnel mais aussi vers la victoire du jeu 
(Cependant, il ne peut pas planifier !).

Après cette étape, ils ont approché la fonction de valeur d'une version un peu plus bruyante de la politique apprise, par régression 
(l'entrée est le tableau d'état et la cible le résultat du jeu).
Vous pouvez utiliser ce réseau pour affecter l'évaluation des nœuds de feuille.

Conceptuellement parlant, le réseau de politiques vous donne une probabilité sur les actions, mais cela n'indique pas que vous finirez dans un bon, pour gagner le jeu,
état. AlphaGo a eu quelques "angles morts" et pendant le tournoi a fait quelques très mauvais coups mais aussi un coup exceptionnel qu'un humain n'aurait jamais pu penser.

Enfin, vous pouvez utiliser votre algorithme de planification (MCTS) en combinaison avec ces filets.
"""


import numpy as np
import tensorflow as tf


class PolicyValueNet():
    def __init__(self, board_size , model_file=None):
        self.board_width = board_size
        self.board_height = board_size

        # Define the tensorflow neural network
        #  Input:
        self.input_states = tf.placeholder(
                tf.float32, shape=[None, 4, board_height, board_width])
        self.input_state = tf.transpose(self.input_states, [0, 2, 3, 1])
        #  Common Networks Layers
        self.conv1 = tf.layers.conv2d(inputs=self.input_state,
                                      filters=32, kernel_size=[3, 3],
                                      padding="same", data_format="channels_last",
                                      activation=tf.nn.relu)
        self.conv2 = tf.layers.conv2d(inputs=self.conv1, filters=64,
                                      kernel_size=[3, 3], padding="same",
                                      data_format="channels_last",
                                      activation=tf.nn.relu)
        self.conv3 = tf.layers.conv2d(inputs=self.conv2, filters=128,
                                      kernel_size=[3, 3], padding="same",
                                      data_format="channels_last",
                                      activation=tf.nn.relu)
        # Action Networks
        self.action_conv = tf.layers.conv2d(inputs=self.conv3, filters=4,
                                            kernel_size=[1, 1], padding="same",
                                            data_format="channels_last",
                                            activation=tf.nn.relu)
        # Flatten the tensor
        self.action_conv_flat = tf.reshape(
                self.action_conv, [-1, 4 * board_height * board_width])
        # Full connected layer, the output is the log probability of moves
        # on each slot on the board
        self.action_fc = tf.layers.dense(inputs=self.action_conv_flat,
                                         units=board_height * board_width,
                                         activation=tf.nn.log_softmax)
        # Evaluation Networks
        self.evaluation_conv = tf.layers.conv2d(inputs=self.conv3, filters=2,
                                                kernel_size=[1, 1],
                                                padding="same",
                                                data_format="channels_last",
                                                activation=tf.nn.relu)
        self.evaluation_conv_flat = tf.reshape(
                self.evaluation_conv, [-1, 2 * board_height * board_width])
        self.evaluation_fc1 = tf.layers.dense(inputs=self.evaluation_conv_flat,
                                              units=64, activation=tf.nn.relu)
        # output the score of evaluation on current state
        self.evaluation_fc2 = tf.layers.dense(inputs=self.evaluation_fc1,
                                              units=1, activation=tf.nn.tanh)

        # Define the Loss function
        #  Label: the array containing if the game wins or not for each state
        self.labels = tf.placeholder(tf.float32, shape=[None, 1])
        # Predictions: the array containing the evaluation score of each state
        # which is self.evaluation_fc2
        # Value Loss function
        self.value_loss = tf.losses.mean_squared_error(self.labels,
                                                       self.evaluation_fc2)
        # Policy Loss function
        self.mcts_probs = tf.placeholder(
                tf.float32, shape=[None, board_height * board_width])
        self.policy_loss = tf.negative(tf.reduce_mean(
                tf.reduce_sum(tf.multiply(self.mcts_probs, self.action_fc), 1)))
        # L2 penalty (regularization)
        l2_penalty_beta = 1e-4
        vars = tf.trainable_variables()
        l2_penalty = l2_penalty_beta * tf.add_n(
            [tf.nn.l2_loss(v) for v in vars if 'bias' not in v.name.lower()])
        # Add up to be the Loss function
        self.loss = self.value_loss + self.policy_loss + l2_penalty

        # Define the optimizer we use for training
        self.learning_rate = tf.placeholder(tf.float32)
        self.optimizer = tf.train.AdamOptimizer(
                learning_rate=self.learning_rate).minimize(self.loss)

        # Make a session
        self.session = tf.Session()

        # calc policy entropy, for monitoring only
        self.entropy = tf.negative(tf.reduce_mean(
                tf.reduce_sum(tf.exp(self.action_fc) * self.action_fc, 1)))

        # Initialize variables
        init = tf.global_variables_initializer()
        self.session.run(init)

        # For saving and restoring
        self.saver = tf.train.Saver()
        if model_file is not None:
            self.restore_model(model_file)

    def policy_value(self, state_batch):
        """
        input: a batch of states
        output: a batch of action probabilities and state values
        """
        log_act_probs, value = self.session.run(
                [self.action_fc, self.evaluation_fc2],
                feed_dict={self.input_states: state_batch}
                )
        act_probs = np.exp(log_act_probs)
        return act_probs, value

    def policy_value_fn(self, board):
        """
        input: board
        output: a list of (action, probability) tuples for each available
        action and the score of the board state
        """
        legal_positions = board.availables
        current_state = np.ascontiguousarray(board.current_state().reshape(
                -1, 4, self.board_width, self.board_height))
        act_probs, value = self.policy_value(current_state)
        act_probs = zip(legal_positions, act_probs[0][legal_positions])
        return act_probs, value

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        """perform a training step"""
        winner_batch = np.reshape(winner_batch, (-1, 1))
        loss, entropy, _ = self.session.run(
                [self.loss, self.entropy, self.optimizer],
                feed_dict={self.input_states: state_batch,
                           self.mcts_probs: mcts_probs,
                           self.labels: winner_batch,
                           self.learning_rate: lr})
        return loss, entropy

    def save_model(self, model_path):
        self.saver.save(self.session, model_path)

    def restore_model(self, model_path):
        self.saver.restore(self.session, model_path)
