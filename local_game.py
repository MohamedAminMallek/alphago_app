import Go_Board
import time
import random
import MCTS_GO


board = Go_Board.Our_Board(board_size=9)

while(not board.game_over()):
    
    
    moves = board.get_legal_moves()
    move = moves[random.randint(0,len(moves))-1]
    board.push(move)
    
    board.print()

    move = MCTS_GO.MCTS(board,board.next)
    #print(move,board.next)
    board.push(move)
    
    board.print()