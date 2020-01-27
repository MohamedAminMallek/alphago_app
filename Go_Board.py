import go as go
import numpy as np

class Our_Board(go.Board):

    def __init__(self,board_size=11):
        super(Our_Board,self).__init__(board_size)
        self.last_move = None
        self.game_is_over = 0 #1 if resign and 2 if two pass
        # ....
    
    def get_legal_moves(self):
        moves = []
        
        #empty position
        for i in range(1,self.board_size+1):
            for j in range(1,self.board_size+1):
                stone = self.search(point=(j,i))
                if type(stone) == list:
                    moves.append((j,i))
    
        #block suicide only when capture
        for move in moves:
            neighboring = [(move[0]-1,move[1]),
                            (move[0]+1,move[1]),
                            (move[0],move[1]-1),
                            (move[0],move[1]+1)]
            valid_move = False
            neighboring_stone = []
            for neighbor in neighboring:
                if not 0 < neighbor[0] <= self.board_size or not 0 < neighbor[1] <= self.board_size:
                    neighboring.remove(neighbor)
                else:
                    stone = self.search(point=neighbor)
                    if type(stone) == list:
                        valid_move = True
                        break
                    else:
                        neighboring_stone.append(stone)
            count_neighbor = 0
            if not valid_move:
                for stone in neighboring_stone:
                    # remove eye move
                    if stone.color == self.next:
                        count_neighbor+=1
           
                    if stone.color == self.next and len(stone.liberties)>1:
                        valid_move = True
                    if stone.color != self.next and len(stone.liberties)==1:
                        valid_move = True
                # remove eye move
                if count_neighbor == len(neighboring_stone):
                    valid_move = False
            
            if not valid_move:
                moves.remove(move)

        # add filter on moves
        # ....  
    
        return moves
    
    def game_over(self):
        return True if ((self.game_is_over>0) or len(self.get_legal_moves())==0) else False
    
    def push(self,point):

        #check if resign
        if point == (-2,-2):
            self.game_is_over = 1
            return
        
        #check if 2 pass
        if self.last_move == point and point == (-1,-1):
            self.game_is_over = 2
            return


        # check if pass
        if point == (-1,-1):
            self.turn()
            self.last_move = point
            return
        
        stone = self.search(point=point)
        if not stone:
            added_stone = go.Stone(self, point, self.turn())
            self.update_liberties(added_stone)
        self.last_move = point

    def score(self):
        nbBlack = 0
        nbWhite = 0
        for i in range(1,self.board_size+1):
            for j in range(1,self.board_size+1):
                stone = self.search(point=(j,i))
                if type(stone) != list:
                    if stone.color == (255,255,255):
                        nbWhite+=1
                    else:
                        nbBlack+=1
        return (nbBlack,nbWhite)
    def get_matrix(self):

        matrix = np.zeros(shape=(self.board_size,self.board_size),dtype=int)
        for i in range(1,self.board_size+1):
            for j in range(1,self.board_size+1):
                stone = self.search(point=(j,i))
                matrix[i-1][j-1] = ((1 if stone.color==(0,0,0) else -1) if (type(stone) != list) else 0)
        return matrix


    def print(self):
        for i in range(self.board_size+1):
            print('_',end=' ')
        print('')
        
        for i in range(1,self.board_size+1):
            for j in range(1,self.board_size+1):
                stone = self.search(point=(j,i))
                _str = (('X' if stone.color==(0,0,0) else 'O') if (type(stone) != list) else '.')
                print(_str,end=' ')
            print('')

        for i in range(self.board_size+1):
            print('_',end=' ')
        print('')
        print('')
