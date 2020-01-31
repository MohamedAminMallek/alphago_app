import copy
from random import randint
import numpy as np
import sys
import math 
from utils import count_points

from tensorflow import keras
new_model = keras.models.load_model('models/model_'+str(9)+'_'+str(30000)+'.h5')


Black_color = (0, 0, 0)
White_color = (255, 255, 255)

class Node_MCTS:
    def __init__(self,parent,board):
        self.parent = parent
        self.nb_win_black = 0
        self.nb_win_white = 0
        self.nb_visits = 0
        self.children = []
        self.board = board

    def get_next_board_randomly(self):
        legal_moves = self.board.get_legal_moves()
        if len(legal_moves) == 0:
            return None
        move =  legal_moves[randint(0,len(legal_moves)-1)]
        new_board = copy.deepcopy(self.board)  
        new_board.push(move)
        return new_board

def selection(root,color):
    
    aux = root
    while len(aux.children)>0:
        best_score = sys.maxsize*-1
        best_node = None
        for node in aux.children:
            score = node.nb_win_black - node.nb_win_white
            score = -score if color == White_color else score
            if score>best_score:
                best_score = score
                best_node = node
        rand = np.random.rand(1)[0]
        if rand>0.8:
            aux = expansion(aux)
        else:
            aux = best_node
    
    return aux

def expansion(root):
    board = root.get_next_board_randomly()
    if board == None:
        return None
    new_node = Node_MCTS(root,board)
    root.children.append(new_node)
    return new_node

def get_coord(pred):
    return pred//9,pred%9
def predict_move(board,player):
    player = 'b' if player == (0,0,0) else 'w'
    board = board.get_matrix()
    board = board*-1 if player == 'w' else board

    board = board.reshape(1,9,9,1)

    pred = new_model.predict(board)[0]
    
    top_3_pred =  pred.argsort()[-5:][::-1]
    moves = [get_coord(p) for p in top_3_pred]
    #print(moves)
    return moves

def simulation(node):
    print("begin of simulation ...")
    r = 0
    b = 0
    while not node.board.game_over() and ((node.board.score()[0]+node.board.score()[1])/(node.board.board_size**2))<0.6 :
        
        moves = predict_move(node.board,node.board.turn())
        
        legal_moves = node.board.get_legal_moves()
        move = None
        for possible_move in moves:
            if possible_move in legal_moves:
                move = possible_move
                break

        if move is None:
            move =  legal_moves[randint(0,len(legal_moves)-1)]
            r = r + 1
        else:
            b = b + 1
            
        node.board.push(move)

    
    print("simulation with",r,"random moves and ",b,"correct moves")

    score = node.board.score()
    #node.board.print()
    #print("Score from utils",score)

    result = score[0] - score[1]
    #print("end of simulation")
    if result > 0:
        return (1,0)
    else:
        if result<0:
            return (0,1)
        else:
            return (0,0)

def backpropagation(node,result):
    
    while node != None:
        node.nb_visits+=1
        node.nb_win_black += result[0]
        node.nb_win_white += result[1]
        node = node.parent
def best_child(root,color):
    best_score = sys.maxsize*-1
    best_node = None
    
    for node in root.children:
        
        reward = 0

        if color == White_color:
            temp_score = node.nb_win_white / (node.nb_visits)
        else:
            temp_score = node.nb_win_black / (node.nb_visits)
        
        reward = temp_score
        
        score = reward + 2*0.1*math.sqrt(2*math.log(node.parent.nb_visits)/node.nb_visits)
        
        #print(score , reward, 'nb win black',node.nb_win_black,'nb win white',node.nb_win_white,'nb visits',node.nb_visits,'parent',node.parent.nb_visits)
        if score>best_score:
            best_score = score
            best_node = node

    print("Best Score = ",best_score,"Black win ",str(best_node.nb_win_black)+" vs ","White win ",str(best_node.nb_win_white))

    move = best_node.board.last_move

    return move if move != None else (color,-1,-1)

def MCTS(board,color,resources_left=10):
    root = Node_MCTS(None,board)
    while(resources_left>0):
        node = selection(root,color)
        new_node = expansion(node)
        if new_node == None:
            resources_left-=1
            print("withou simulation")
            continue
        result = simulation(copy.deepcopy(new_node))
        backpropagation(new_node,result)
        resources_left-=1
    
    move = best_child(root,color)
    return move
