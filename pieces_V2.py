"""
This library is meant to be an optimized version of the more abstract pieces library.
This library will be used for faster move searches while the other one will be used for
player games.

- only require enemy unculled moves, player culled moves
"""
  
def new_move(GRID, origin, target, piece, enpassant_pawn, castling_possible, castle_long, castle_short, king, checking_enpassant=False, checking_castling=False):

    """
    make a sim function: get pos of pieces if a move was to be made,
    if king is still attacked, return false. do this in the in_check method

    if this is run by each piece, the logic for clicking different squares could be much
    simpler. what would need to change are the flags here. each move could be tested against the is_legal_position()
    method.
    castling would probably be done the same by checking the flags here, but instead they would be
    computed in the kings legal move thing
    """

    # debug
    # if check_castling and checking_castling:
    #     pass
    new_grid = []

    # basically a more retarded deepcopy
    for row in GRID:
        new_row = []
        for sq in row:
            new_row.append(sq)
        new_grid.append(new_row)

    # if check_castling and checking_castling:
    #     print('\n\n')
    #     [print(i) for i in new_grid]

    y1, x1 = origin
    y2, x2 = target

    # it doesnt matter which one, we will know depending on whose turn it is
    if piece in ['wk', 'bk']:
        king = (y2, x2)

    if checking_castling:  # this does not run if the enemy king is simply checking its legal moves

        # the king has moved => castling is not possible
        if piece == 'wk':
            castle_long = castle_short = False
            castling_possible = False
        
        elif piece == 'wr':

            # if long
            if x1 == 0 and y1 == 7:
                castle_long = False
                

            # if short
            elif x1 == 7 and y1 == 7:
                castle_short = False
        
        elif piece == 'br':

            # if long for black
            if x1 == 0 and y1 == 0:
                castle_long = False

            # if short for black
            elif x1 == 7 and y1 == 0:
                castle_short = False

        # if a piece was moved to the rook's home - can only happen if rook is getting captured or if the rook has already moved
        if x2 == 0 and y2 == 0:
            castle_long = False
            
        elif x2 == 0 and y2 == 7:
            castle_long = False
            
        elif x2 == 7 and y2 == 7:
            castle_short = False
            
        elif x2 == 7 and y2 == 0:
            castle_short = False
            
    
    # check for enpassant
    if checking_enpassant:  # enpassant pawn is getting changed so I need to make a function that remembers the pawn that moved and save it after the new move has been created
        
        # assign en passant
        if piece[1] == 'p':

            if y1 == 6 and y2 == 4:
                enpassant_pawn = (y2, x2)

            elif y1 == 1 and y2 == 3:
                enpassant_pawn = (y2, x2)

            else:
                enpassant_pawn = None
            
        else:
            enpassant_pawn = None

    # for enpassant        
    if piece == 'wp':
        # if enpassant has been played as white
        if y1 == 3 and y2 == 2:

            if x2 == x1 - 1 and new_grid[y2][x1 - 1] == '00':
                new_grid[y1][x1 - 1] = '00'

            elif x2 == x1 + 1 and new_grid[y2][x1 + 1] == '00':
                new_grid[y1][x1 + 1] = '00'
    
    if piece == 'bp':
        # if enpassant has been played as black
        if y1 == 4 and y2 == 5:
            
            if x2 == x1 - 1 and new_grid[y2][x1 - 1] == '00':
                new_grid[y1][x1 - 1] = '00'

            elif x2 == x1 + 1 and new_grid[y2][x1 + 1] == '00':
                new_grid[y1][x1 + 1] = '00'

    new_grid[y1][x1] = '00'
    new_grid[y2][x2] = piece

    # do castling execution here
    if checking_castling:
        if piece == 'wk':
            if x1 == 4 and y1 == 7:
                if x2 == 6 and y2 == 7:  # castled short for white
                    castle_short = False
                    castle_long = False

                    new_grid[7][7] = '00'
                    new_grid[7][5] = 'wr'

                    castling_possible = False

                elif x2 == 2 and y2 == 7:  # castled long for white
                    castle_long = False
                    castle_short = False

                    new_grid[7][0] = '00'
                    new_grid[7][3] = 'wr'

                    castling_possible = False

        elif piece == 'bk':
            if x1 == 4 and y1 == 0:
                if x2 == 6 and y2 == 0:  # castled short for black
                    castle_short = False
                    castle_long = False

                    new_grid[0][7] = '00'
                    new_grid[0][5] = 'br'

                    castling_possible = False

                elif x2 == 2 and y2 == 0:  # castled long for black
                    castle_long = False
                    castle_short = False

                    new_grid[0][0] = '00'
                    new_grid[0][3] = 'br'

                    castling_possible = False

    # if check_castling and checking_castling:
    #     [print(i) for i in new_grid]

    return new_grid, castling_possible, castle_long, castle_short, enpassant_pawn, king

  
def get_pieces_list(grid):
    white_pieces = []
    black_pieces = []

    for i, row in enumerate(grid):
        for j, col in enumerate(row):
            if col[0] == 'w':
                white_pieces.append((i, j))
            elif col[0] == 'b':
                black_pieces.append((i, j))

    return white_pieces, black_pieces

  
def illegal_moves(king, grid, potential_moves):

        bad_moves = []  # list of illegal moves
        white_turn = grid[king[0]][king[1]][0] == 'w'
        origin = potential_moves[0]
        
        piece_id = grid[origin[0]][origin[1]]
        for move in potential_moves[1]:
            # print(potential_moves)
            # move[0] is the origin, move[1] is the target, grid[move[1][0]][move[1][1]] just give the piece id
            future_state, _, _, _, _, king = new_move(grid, origin, move, piece_id, None, None, None, None, king)
            future_white_pieces, future_black_pieces = get_pieces_list(future_state)

            # choose pieces list based on turn
            opposite_pieces_list = future_black_pieces if white_turn else future_white_pieces
            
            # check each position
            if not is_legal_position(future_state, opposite_pieces_list, king):
                bad_moves.append((origin, move))

        # print(f'PIECE: {selected_square.piece}')
        # print('\nPOTENTIAL MOVES')
        # [print(k) for k in potential_moves]
        # print('\nBAD MOVES:')
        # [print(k) for k in bad]
        
        return bad_moves

  
def is_legal_position(grid, enemy_pieces_list, king):  # squares for new game state, player_pieces_list to check moves against the players king, enemy_pieces_list for all legal moves of the opposite player
        
        """
        make a state of the future board using the new grid given.
        if the players king is exposed by new state legal moves, return False
        if the players king is not, then it is a legal move, return True
        call this function in a loop of all the legal moves that can be made by the piece
        """
        # print('\n\n')
        # [print(i) for i in grid]
        y, x = king
        # inshaallah this works
        if grid[y][x][1] != 'k': 
            
            return False  # two kings will never have the opportunity to capture each other. but if theres a bug in my code with kings involved, then ill know where to look
        # friendly_colour = grid[y][x][0]

        # this method is preferred, storing pieces as an x, y pos in a list
        for piece in enemy_pieces_list:
            y, x = piece
            identity = grid[y][x][1]
            colour = grid[y][x][0]
            # these bools are really just placeholders as these values do not need to be accessed by the enemy
            for move in match_piece_moves(identity, colour, (y, x), grid, None, None, False, False, False, castling=False)[1]:

                # this should be faster than appending. king and move are both just x, y positions
                if king == move:
                    return False

        # for i, row in enumerate(grid):
        #     for j, col in enumerate(row):
        #         if col[0] != friendly_colour:
        #             for move in match_piece_moves(col[1], col[0], (i, j), grid, None):
        #                 enemy_moves_unculled.append(move)
                
        # check if king is in the enemies move list
        
        return True

   
def check_castling(king, grid, enemy_moves, castling_possible, castle_long, castle_short, longue=False, short=False):
        """
        king will be the king position
        enemy moves will be the unculled opposite moves
        """
        y = 7 if grid[king[0]][king[1]][0] == 'w' else 0  # determines the rank

        # king or both rooks have moved
        if not castling_possible:
            # print("RETURNING FALSE", 1)
            return False

        if king in enemy_moves:
            # print("RETURNING FALSE", 2)
            return False
        
        if short:
            if not castle_short:
                # print("RETURNING FALSE", 3)
                return False

            if (y, 5) in enemy_moves or (y, 6) in enemy_moves:
                # print("RETURNING FALSE", 4)
                return False
            
            if grid[y][5] != '00' or grid[y][6] != '00':
                # [print(i) for i in grid]
                # print("RETURNING FALSE", 5, y)
                return False
            
        elif longue:  # the word long was already taken  # hmm so turns out its actually okay to use it, but it can get distracting maybe since its red in colour
            if not castle_long:
                # print("RETURNING FALSE", 6)
                return False

            if (y, 3) in enemy_moves or (y, 2) in enemy_moves:
                # print("RETURNING FALSE", 7)
                return False
            
            if grid[y][3] != '00' or grid[y][2] != '00' or grid[y][1] != '00':
                # [print(i) for i in grid]
                # print("RETURNING FALSE", 8, y)
                return False
              
        return True

def pawn_moves(colour, grid, pos, enpassant):

    """
    this function uses only lists and returns origin, target coords
    """

    j, i = pos  # y, x: 'i' usually refers to the y pos, but in this case (b/c im too lazy to change it), it means x here

    all_moves = []

    if colour == 'w':

        if j > 0 and grid[j - 1][i] == '00':
            all_moves.append((j - 1, i))
            if j == 6 and grid[j - 2][i] == '00':
                all_moves.append((j - 2, i))

        # capturing
        if (j > 0 and i > 0 and grid[j - 1][i - 1] != '00' and grid[j - 1][i - 1][0] == 'b') or (j == 3 and i > 0 and (j, i - 1) == enpassant):
            all_moves.append((j - 1, i - 1))

        if (j > 0 and i < 7 and grid[j - 1][i + 1] != '00' and grid[j - 1][i + 1][0] == 'b') or (j == 3 and i < 7 and (j, i + 1) == enpassant):
            all_moves.append((j - 1, i + 1))

    elif colour == 'b':

        if j < 7 and grid[j + 1][i] == '00':
            all_moves.append((j + 1, i))
            if j == 1 and grid[j + 2][i] == '00':
                all_moves.append((j + 2, i))

        if (j < 7 and i > 0 and grid[j + 1][i - 1] != '00' and grid[j + 1][i - 1][0] == 'w') or (j == 4 and i > 0 and (j, i - 1) == enpassant):
            all_moves.append((j + 1, i - 1))

        if (j < 7 and i < 7 and grid[j + 1][i + 1] != '00' and grid[j + 1][i + 1][0] == 'w') or (j == 4 and i < 7 and (j, i + 1) == enpassant):
            all_moves.append((j + 1, i + 1))

    return pos, all_moves

   
def king_moves(colour, grid, pos, castling, enemy_moves, castling_possible, castling_long, castling_short):
    
    all_moves = []

    j, i = pos # grid checks y, then x, hence [j] then [i]

    if i > 0:
        s = grid[j][i - 1] # s is the tile on the board --> class object
        if s == '00':
            all_moves.append((j, i - 1))
        elif s[0] != colour:
            all_moves.append((j, i - 1))

    if i < 7:
        s = grid[j][i + 1]
        if s == '00':
            all_moves.append((j, i + 1))
        elif s[0] != colour:
            all_moves.append((j, i + 1))

    if j > 0:
        s = grid[j - 1][i]
        if s == '00':
            all_moves.append((j - 1, i))
        elif s[0] != colour:
            all_moves.append((j - 1, i))

    if j < 7:
        s = grid[j + 1][i]
        if s == '00':
            all_moves.append((j + 1, i))
        elif s[0] != colour:
            all_moves.append((j + 1, i))
    # diagonals
    if i > 0 and j > 0:
        s = grid[j - 1][i - 1]
        if s == '00':
            all_moves.append((j - 1, i - 1))
        elif s[0] != colour:
            all_moves.append((j - 1, i - 1))

    if i > 0 and j < 7:
        s = grid[j + 1][i - 1]
        if s == '00':
            all_moves.append((j + 1, i - 1))
        elif s[0] != colour:
            all_moves.append((j + 1, i - 1))

    if i < 7 and j > 0:
        s = grid[j - 1][i + 1]
        if s == '00':
            all_moves.append((j - 1, i + 1))
        elif s[0] != colour:
            all_moves.append((j - 1, i + 1))

    if i < 7 and j < 7:
        s = grid[j + 1][i + 1]
        if s == '00':
            all_moves.append((j + 1, i + 1))
        elif s[0] != colour:
            all_moves.append((j + 1, i + 1))

    if castling:
        if check_castling((j, i), grid, enemy_moves, castling_possible, castling_long, castling_short, longue=True):
            all_moves.append((j, i - 2))

        if check_castling((j, i), grid, enemy_moves, castling_possible, castling_long, castling_short, short=True):
            all_moves.append((j, i + 2))


    return pos, all_moves

   
def bishop_moves(colour, grid, pos):
    all_moves = []

    j, i = pos

    to_right = 8 - i
    to_left = 1 + i
    to_up = 1 + j
    to_down = 8 - j

    # one liners, nw is to left if to left is the lesser value, otherwise is to up
    nw = to_left if to_left < to_up else to_up
    ne = to_right if to_right < to_up else to_up
    sw = to_left if to_left < to_down else to_down
    se = to_right if to_right < to_down else to_down

    if colour == 'w':
        pass

    for iterator in range(1, nw):
        
        s = grid[j - iterator][i - iterator]
        
        if s == '00':
            all_moves.append((j - iterator, i - iterator))
        elif s[0] != colour:
            all_moves.append((j - iterator, i - iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, sw):
        s = grid[j + iterator][i - iterator]
        if s == '00':
            all_moves.append((j + iterator, i - iterator))
        elif s[0] != colour:
            all_moves.append((j + iterator, i - iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, ne):
        s = grid[j - iterator][i + iterator]
        if s == '00':
            all_moves.append((j - iterator, i + iterator))
        elif s[0] != colour:
            all_moves.append((j - iterator, i + iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, se):
        s = grid[j + iterator][i + iterator]
        if s == '00':
            all_moves.append((j + iterator, i + iterator))
        elif s[0] != colour:
            all_moves.append((j + iterator, i + iterator))
            break
        elif s[0] == colour:
            break
    
    return pos, all_moves

   
def rook_moves(colour, grid, pos):
    all_moves = []

    j, i = pos

    to_right = 8 - i
    to_left = 1 + i
    to_up = 1 + j
    to_down = 8 - j

    for iterator in range(1, to_right): # FIX THESE
        s = grid[j][i + iterator]

        if s == '00':
            all_moves.append((j, i + iterator))

        elif s[0] != colour:
            all_moves.append((j, i + iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, to_left):
        s = grid[j][i - iterator]

        if s == '00':
            all_moves.append((j, i - iterator))

        elif s[0] != colour:
            all_moves.append((j, i - iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, to_up):
        s = grid[j - iterator][i]

        if s == '00':
            all_moves.append((j - iterator, i))

        elif s[0] != colour:
            all_moves.append((j - iterator, i))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, to_down):
        s = grid[j + iterator][i]

        if s == '00':
            all_moves.append((j + iterator, i))

        elif s[0] != colour:
            all_moves.append((j + iterator, i))
            break
        elif s[0] == colour:
            break

    return pos, all_moves

   
def queen_moves(colour, grid, pos):
    all_moves = []

    j, i = pos

    to_right = 8 - i
    to_left = 1 + i
    to_up = 1 + j
    to_down = 8 - j

    # one liners, nw is to left if to left is the lesser value, otherwise is to up
    nw = to_left if to_left < to_up else to_up
    ne = to_right if to_right < to_up else to_up
    sw = to_left if to_left < to_down else to_down
    se = to_right if to_right < to_down else to_down

    for iterator in range(1, nw):
        s = grid[j - iterator][i - iterator]
        if s == '00':
            all_moves.append((j - iterator, i - iterator))
        elif s[0] != colour:
            all_moves.append((j - iterator, i - iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, sw):
        s = grid[j + iterator][i - iterator]
        if s == '00':
            all_moves.append((j + iterator, i - iterator))
        elif s[0] != colour:
            all_moves.append((j + iterator, i - iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, ne):
        s = grid[j - iterator][i + iterator]
        if s == '00':
            all_moves.append((j - iterator, i + iterator))
        elif s[0] != colour:
            all_moves.append((j - iterator, i + iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, se):
        s = grid[j + iterator][i + iterator]
        if s == '00':
            all_moves.append((j + iterator, i + iterator))
        elif s[0] != colour:
            all_moves.append((j + iterator, i + iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, to_right): # FIX THESE
        s = grid[j][i + iterator]

        if s == '00':
            all_moves.append((j, i + iterator))

        elif s[0] != colour:
            all_moves.append((j, i + iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, to_left):
        s = grid[j][i - iterator]

        if s == '00':
            all_moves.append((j, i - iterator))

        elif s[0] != colour:
            all_moves.append((j, i - iterator))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, to_up):
        s = grid[j - iterator][i]

        if s == '00':
            all_moves.append((j - iterator, i))

        elif s[0] != colour:
            all_moves.append((j - iterator, i))
            break
        elif s[0] == colour:
            break

    for iterator in range(1, to_down):
        s = grid[j + iterator][i]

        if s == '00':
            all_moves.append((j + iterator, i))

        elif s[0] != colour:
            all_moves.append((j + iterator, i))
            break
        elif s[0] == colour:
            break

    return pos, all_moves

   
def knight_moves(colour, grid, pos):
    all_moves = []

    j, i = pos  # y, x

    if j > 1 and i > 0:
        s = grid[j - 2][i - 1] # super top left
        if s == '00':
            all_moves.append((j - 2, i - 1))
        elif s[0] != colour:
            all_moves.append((j - 2, i - 1))

    if j > 1 and i < 7:
        s = grid[j - 2][i + 1] # super top right
        if s == '00':
            all_moves.append((j - 2, i + 1))
        elif s[0] != colour:
            all_moves.append((j - 2, i + 1))

    if j < 6 and i > 0:
        s = grid[j + 2][i - 1] # super bottom left
        if s == '00':
            all_moves.append((j + 2, i - 1))
        elif s[0] != colour:
            all_moves.append((j + 2, i - 1))

    if j < 6 and i < 7:
        s = grid[j + 2][i + 1] # super bottom right
        if s == '00':
            all_moves.append((j + 2, i + 1))
        elif s[0] != colour:
            all_moves.append((j + 2, i + 1))

    # Flip sides - 'flip' because values invert in relation to the above
    if j > 0 and i > 1:
        s = grid[j - 1][i - 2] # flip top left
        if s == '00':
            all_moves.append((j - 1, i - 2))
        elif s[0] != colour:
            all_moves.append((j - 1, i - 2))

    if j > 0 and i < 6:
        s = grid[j - 1][i + 2] # flip top right
        if s == '00':
            all_moves.append((j - 1, i + 2))
        elif s[0] != colour:
            all_moves.append((j - 1, i + 2))

    if j < 7 and i > 1:
        s = grid[j + 1][i - 2] # flip bottom left
        if s == '00':
            all_moves.append((j + 1, i - 2))
        elif s[0] != colour:
            all_moves.append((j + 1, i - 2))

    if j < 7 and i < 6:
        s = grid[j + 1][i + 2] # flip bottom right
        if s == '00':
            all_moves.append((j + 1, i + 2))
        elif s[0] != colour:
            all_moves.append((j + 1, i + 2))

    return pos, all_moves

  
def match_piece_moves(piece, colour, pos_yx, grid, enpassant_yx, enemy_moves, castling_possible, castling_long, castling_short, castling=False):

    """
    this function will handle all piece generating moves based on the grid.
    colours will be handled separately, with the enemy generating first, then the player.
    """

    match piece:
        case "0":
            return ('00', [])

        case "p":
            return pawn_moves(colour, grid, pos_yx, enpassant_yx)

        case "b":
            return bishop_moves(colour, grid, pos_yx)

        case "r":
            return rook_moves(colour, grid, pos_yx)

        case "n":
            return knight_moves(colour, grid, pos_yx)

        case "k":
            return king_moves(colour, grid, pos_yx, castling, enemy_moves, castling_possible, castling_long, castling_short)

        case "q":
            return queen_moves(colour, grid, pos_yx)

        case _:
            return (None, [])
