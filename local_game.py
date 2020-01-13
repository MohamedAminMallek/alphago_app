import Go_Board
import time
import random


board = Go_Board.Our_Board(board_size=9)

while(not board.game_over()):
    time.sleep(1)
    
    moves = board.get_legal_moves()
    move = moves[random.randint(0,len(moves))-1]
    #point = (random.randint(1,9),random.randint(1,9))
    #print(point)
    board.push(move)
    board.print()
