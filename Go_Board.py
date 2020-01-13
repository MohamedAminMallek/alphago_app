import go as go

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
                if type(stone) != type:
                    moves.append((j,i))
    
        # add filter on moves
        # ....    
    
        return moves

        pass
    
    def game_over(self):
        pass
    
    def push(self,point):

        #check if resign
        if point == (-2,-2):
            self.game_is_over = 1
            return
        
        #check if 2 pass
        if self.last_move == point:
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
