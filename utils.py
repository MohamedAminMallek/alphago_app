def count_points(Board):
    noirs = 0
    blancs = 7.5
    for i in range(1, Board.board_size+1):
        for j in range (1, Board.board_size+1):
            stone = Board.search(point=(i,j))
            if type(stone) == list:
                 voisins_blancs, voisins_noirs = 0, 0
                 neighboring = stone.neighbors()
                 stones = Board.search(points=neighboring)
                 for stone in stones:
                     if stone.color == (0,0,0):
                         voisins_noirs += 1
                     else:
                         voisins_blancs +=1
                 if voisins_noirs == 0 and voisins_blancs != 0:
                    blancs += 1
                 if voisins_noirs != 0 and voisins_blancs == 0:
                     noirs += 1
            elif stone.color == (0,0,0):
                noirs += 1
            else:
                blancs += 1

    return (noirs, blancs)
