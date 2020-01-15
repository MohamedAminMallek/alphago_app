def get_neighbors(point,Board):
    neighboring = [(point[0]-1,point[1]),
                    (point[0]+1,point[1]),
                    (point[0],point[1]-1),
                    (point[0],point[1]+1)]
    for neighbor in neighboring:
        if not 0 < neighbor[0] <= Board.board_size or not 0 < neighbor[1] <= Board.board_size:
            neighboring.remove(neighbor)
    return neighboring

def count_points(Board):
    noirs = 0
    blancs = 7.5
    for i in range(1, Board.board_size+1):
        for j in range (1, Board.board_size+1):
            stone = Board.search(point=(i,j))
            if type(stone) == list:
                 stone = (i,j)
                 voisins_blancs, voisins_noirs = 0, 0
                 neighboring = get_neighbors(stone,Board)
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
