import random; import time; from timeit import timeit

from pieces_V2 import *
from positions_V2 import *

from pieces import *  # currently is basically depreciated

"""
TODO: OPTIMIZE, OPTIMIZE, OPTIMIZE

- stop running the valid moves method like 77 times
- start storing king position
- make a pos attr for each piece so that the program doesnt have to do so much division
- only use heavy objects/abstractions when needed
- try match/case for the mk pieces function
"""

def mk_pieces(game, piece, x, y, grid):

    match piece:

        case 'bp':
            return Pawn(game, game.position, x, y, piece[0], piece, grid)

        case 'wp':
            return Pawn(game, game.position, x, y, piece[0], piece, grid)

        case 'br':
            return Rook(game, game.position, x, y, piece[0], piece, grid)

        case 'bn':
            return Knight(game, game.position, x, y, piece[0], piece, grid)

        case 'bb':
            return Bishop(game, game.position, x, y, piece[0], piece, grid)

        case 'bq':
            return Queen(game, game.position, x, y, piece[0], piece, grid)

        case 'bk':
            return King(game, game.position, x, y, piece[0], piece, grid)

        case 'wr':
            return Rook(game, game.position, x, y, piece[0], piece, grid)

        case 'wn':
            return Knight(game, game.position, x, y, piece[0], piece, grid)

        case 'wb':
            return Bishop(game, game.position, x, y, piece[0], piece, grid)

        case 'wq':
            return Queen(game, game.position, x, y, piece[0], piece, grid)

        case 'wk':
            return King(game, game.position, x, y, piece[0], piece, grid)
        
        case _:
            return None


def create_grid(grid, game, pg):

    black_pieces = []
    white_pieces = []

    squares = []
    for i, row in enumerate(grid):  # tile map technique
        a = []  # 'a' is just another list that makes it so the resulting multidimentional list has a de facto x and y value
        for j, col in enumerate(row):
            if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):  # this condition makes the black-white pattern
                square = Square(game, j, i, 'w', pg)
                a.append(square)

            else:
                square = Square(game, j, i, 'g', pg)
                a.append(square)

            new_piece = mk_pieces(game, col, j, i, grid)  # position object, value, x, y, grid
            if new_piece != None:

                square.piece = new_piece

                if new_piece.colour == 'w':
                    white_pieces.append(new_piece)

                else:
                    black_pieces.append(new_piece)

        squares.append(a) # squares is a 2 dimensional list

    return black_pieces, white_pieces, squares

class Position:

    """
    this is for the chess engine to use. each boardstate will be converted to
    a Position object that stores its legal moves, player to move, eval, and
    potentially, the move that was played to reach it (only if immediate child to
    the root node - we dont need all the moves to be stored).
    """

    def __init__(self, 
                 game, 
                 move, 
                 white_turn: bool, 
                 grid, 
                 pg,
                 king_castle_long_white,
                 king_castle_long_black,
                 king_castle_short_black,
                 king_castle_short_white,
                 white_castling_possible,
                 black_castling_possible,
                 enpassant_pawn,
                 white_king,
                 black_king
                 ) -> None:
        
        """
        Test having already calculated different aspects about the node
        in this method before moving onto further calculations. This is
        where the tree search will try to be implemented.

        grid can simulate later positions
        board can derive player and enemy moves as well as
        get scores and such

        maybe the squares and pieces list get initialized here as well?
        this as opposed to passing it in as an argument
        
        could possibly make a different promotions function specialized for
        the chess bots to access and make a decision. the new moves method
        would probably be redone to account for this. its output would
        simply be any of the four possibilies. or maybe the value gets
        decided in a loop and kept as a value? the new move method only
        needs the result of the promotion anyways, so 4 extra positions can 
        easily be simulated by a for loop
        """

        self.game = game
        self.pygame = pg
        self.Xtl = self.game.Xtl
        self.Ytl = self.game.Ytl
        self.white_turn = white_turn

        self.move_number = 0  # default value, gets changed otherwise
        # a clause so that i can cheese the first __init__() call back in main.py
        
        self.move = move
        self.grid = grid  # to make new moves

        # print('time needed to make new grid in pos class')
        # t = time.time()
        self.black_pieces, self.white_pieces, self.board = create_grid(self, self.grid)
        # print(time.time() - t)

        # make a function that updates these values based on the position so that they can be stored when moves are simulated. ie, if in a branch, player decides to castle, they cannot castle later on in that same branch
        self.king_castle_long_white  = king_castle_long_white
        self.king_castle_long_black  = king_castle_long_black
        self.king_castle_short_black = king_castle_short_black
        self.king_castle_short_white = king_castle_short_white
        
        self.white_castling_possible = white_castling_possible
        self.black_castling_possible = black_castling_possible

        self.enpassant_pawn = enpassant_pawn

        if white_king is None or black_king is None:
            for i, row in enumerate(self.grid):
                for j, val in enumerate(row):
                    if val == 'wk':
                        self.white_king = self.board[i][j]

                    if val == 'bk':
                        self.black_king = self.board[i][j]

        else:

            wx, wy = white_king.pos
            self.white_king = self.board[wy][wx]

            bx, by = black_king.pos
            self.black_king = self.board[by][bx]

        self.king = self.white_king if self.white_turn else self.black_king
        

        # print(f'\nIN POSITIONS CLASS: ENPASSANT PAWN: {self.enpassant_pawn}')

        # this goes before the player/enemy pieces assignment so that the enpassant gets saved between assignments
        if self.enpassant_pawn is not None:

            # we use the opposite player's pieces here
            pieces = self.white_pieces if self.move[0].piece.id == 'wp' else self.black_pieces
            # print(f'PIECES LIST: {pieces} USED. WHITE\'S TURN: {self.white_turn}\n')
            for piece in pieces:
                if piece.class_value == 'pawn':
                    if piece.yx_pos == (self.enpassant_pawn[1], self.enpassant_pawn[0]):
                        # print('SETTING ENPASSANT PAWN IN POSITIONS CLASS:\n')
                        piece.enpassant = True
                        # print(f'IN POSITIONS CLASS: PIECE: {piece}')
                        break

        self.player_pieces = self.white_pieces if self.white_turn else self.black_pieces
        self.enemy_pieces = self.black_pieces if self.white_turn else self.white_pieces

        # initialize the moves list
        self.white_moves = []
        self.black_moves = []
        self.white_moves_unculled = []
        self.black_moves_unculled = []

        self.player_moves = []
        self.enemy_moves = []
        self.player_moves_unculled = []
        self.enemy_moves_unculled = []

        self.children = {}
        
        # idk, ill optimize it later with bitboards or something
        # print('\ntime needed to make children')
        # t = time.time()
        for piece in self.player_pieces:
            is_promoting = False
            i = len(self.children)  # ensures no duplicates in the dict

            if piece.class_value == 'king':
                # this requires reprogramming of the valid moves function to work with the Position class
                # print(f'\nTime needed to generate moves: {piece}')
                # t = time.time()
                moves, bad_moves = piece.valid_moves(self.board, cull_illegal_moves=True, add_castling=True)
                for move in moves:
                    self.player_moves_unculled.append(move)

                for move in bad_moves:  # why is appending/removing faster here than in list comps???
                    moves.remove(move)

                for move in moves:
                    self.player_moves.append(move)

                # print(time.time() - t)
            # this can be far better optimized by simply storing the piece id with the moves
            else:
                # for promotions
                if (piece.class_value == 'pawn' and piece.colour == 'w' and piece.yx_pos[0] == 1) or (piece.class_value == 'pawn' and piece.colour == 'b' and piece.yx_pos[0] == 6):
                    # print(f'\nTime needed to generate moves and promotion: {piece}')
                    # t = time.time()
                    future_moves, bad_moves = piece.valid_moves(self.board, cull_illegal_moves=True)
                    for move in future_moves:
                        self.player_moves_unculled.append(move)

                    for move in bad_moves:
                        future_moves.remove(move)

                    for move in future_moves:
                        self.player_moves.append(move)
                    
                    moves = self.promotion(piece, future_moves)
                    is_promoting = True
                    # print(time.time() - t)

                else:
                    # print(f'\nTime needed to generate moves: {piece}')
                    # t = time.time()
                    moves, bad_moves = piece.valid_moves(self.board, cull_illegal_moves=True)
                    for move in moves:
                        self.player_moves_unculled.append(move)

                    for move in bad_moves:
                        moves.remove(move)

                    for move in moves:
                        self.player_moves.append(move)
                    # print(time.time() - t)
            # keep this dict simple so that the program isnt storing/generating like 80 objects each time
            for j, move in enumerate(moves):

                # have an if flag here for promotion? probably
                # idk if this is actually going to work but ig we'll see lol
                if not is_promoting:
                    s = f'{i + j}|({piece.yx_pos}, {piece.id})'  # 'num|((y, x), id)' = move. (y, x) is origin square, move is target square, id is piece being moved
                    self.children[s] = move
                
                else:
                    # move[0] will contain the new piece (object), move[1] will contain the move]

                    identity = move[0]
                    s = f'{i + j}|({piece.yx_pos}, {identity})'
                    self.children[s] = move
            
        
        # assignment here will change the correspondant list as well
        if self.white_turn:
            self.white_moves = self.player_moves
            self.white_moves_unculled = self.player_moves_unculled

            for piece in self.black_pieces:
                moves, bad_moves = piece.valid_moves(self.board)
                for move in moves:
                    self.enemy_moves_unculled.append(move)

                for move in bad_moves:
                    moves.remove(move)

                for move in moves:
                    self.enemy_moves.append(move)

            self.black_moves = self.enemy_moves
            self.black_moves_unculled = self.enemy_moves_unculled

        else:
            self.black_moves = self.player_moves
            self.black_moves_unculled = self.player_moves_unculled

            for piece in self.white_pieces:
                moves, bad_moves = piece.valid_moves(self.board)
                for move in moves:
                    self.enemy_moves_unculled.append(move)

                for move in bad_moves:
                    moves.remove(move)

                for move in moves:
                    self.enemy_moves.append(move)

            self.white_moves = self.enemy_moves
            self.white_moves_unculled = self.enemy_moves_unculled

        # print(self.white_moves)
        # print('\n\n')
        # print(self.black_moves)
        
        # print(time.time() - t)

        #     [print(i) for i in self.grid]
        # print(f'{self.white_turn}: {len(self.children)}\n')

        # origin_square = self.board[move[0].y // self.game.Ytl][move[0].x // self.game.Xtl]
        # move_pos = move[1].pos

        # print(f'\nWHITE\'S TURN TO MOVE: {self.white_turn}')
        # print(f"{self.game.positions_searched} POSITIONS SEARCHED")
        # print(f'CURRENT POSITION BEING SEARCHED:')
        # [print(i) for i in self.grid]
        # print(f'AMOUNT OF CHILDREN IN CURRENT POSITION: {len(self.children)}\n')

    
    def promotion(self, pawn, moves):

        """
        need to somehow take the possible moves and make them
        into the four possibilities and make sure that the new_move
        method knows that the origin square gets cleared and the new square becomes
        the promoted piece. idk how tf im gonna do this ngl. store the piece
        as the new piece in the enumeration iteration? make it a special
        case maybe?
        => i think thats what i need to do
        """

        all_moves = []
        y, x = pawn.yx_pos

        for move in moves:
        
            all_moves.append((f'{pawn.colour}q', move))
            all_moves.append((f'{pawn.colour}r', move))
            all_moves.append((f'{pawn.colour}n', move))
            all_moves.append((f'{pawn.colour}b', move))

        return all_moves

    def checkmate(self, check_insufficient_material=True):



        # checks for insufficient material
        if check_insufficient_material:
            if len(self.player_pieces) <= 2 and len(self.enemy_pieces) <= 2:
                # print(self.player_pieces, self.enemy_pieces)
                if len(self.player_pieces) == 1 and len(self.enemy_pieces) == 1:  # only kings on the board (or else something has gone very, very wrong)
                    return 3

                # ensures that first element is not the king, so that the second piece can be checked
                [king := square for square in self.player_pieces if square.class_value == 'king']
                self.player_pieces.remove(king)
                self.player_pieces.append(king)

                [king := square for square in self.enemy_pieces if square.class_value == 'king']
                self.enemy_pieces.remove(king)
                self.enemy_pieces.append(king)

                other_piece = self.player_pieces[0].class_value
                enemy_other_piece = self.enemy_pieces[0].class_value

                if other_piece == 'knight' or other_piece == 'bishop':
                    if len(self.enemy_pieces) == 1:  # only king
                        return 3
                    
                    if enemy_other_piece == 'knight' or enemy_other_piece == 'bishop':
                        return 3

        # for piece in self.player_pieces:

        #     square = self.board[piece.y // self.Ytl][piece.x // self.Xtl] 
        #     if piece.class_value == 'king':
        #         king = square
        # print(self.player_moves, self.player_moves_unculled)
        if self.player_moves == []:
            # enemy_moves = []
            # for piece in enemy_list:
            #     [enemy_moves.append(move) for move in piece.valid_moves(self.squares)]

            if self.king in self.enemy_moves_unculled:  # checkmate
                
                return 1
            
            # else: stalemate
            return 2
        
        return 0

    def illegal_moves(self, GRID, potential_moves, selected_square):  # selected square is a square object

        bad = []  # list of illegal moves
        for move in potential_moves:  # 'move' is a Square object here

            future_state = self.new_move(GRID, selected_square.pos, move.pos, selected_square.piece.id)
            future_black_pieces, future_white_pieces, future_squares_list = create_grid(self, future_state)

            # choose pieces list based on turn
            opposite_pieces_list = future_black_pieces if self.white_turn else future_white_pieces
            if self.white_turn:
                if selected_square.piece.id == 'wk':
                    king = future_squares_list[move.pos[1]][move.pos[0]]
                else:
                    king = self.king
                opposite_pieces_list = future_black_pieces
                player_pieces_list = future_white_pieces
            else:
                if selected_square.piece.id == 'bk':
                    king = future_squares_list[move.pos[1]][move.pos[0]]
                else:
                    king = self.king
                opposite_pieces_list = future_white_pieces
                player_pieces_list = future_black_pieces
            
            # check each position
            if not self.is_legal_position(future_squares_list, future_state, opposite_pieces_list, king):
                bad.append(move)

        # print(f'PIECE: {selected_square.piece}')
        # print('\nPOTENTIAL MOVES')
        # [print(k) for k in potential_moves]
        # print('\nBAD MOVES:')
        # [print(k) for k in bad]
        
        return bad
    
    def is_legal_position(self, squares, grid, enemy_pieces_list, king):  # squares for new game state, player_pieces_list to check moves against the players king, enemy_pieces_list for all legal moves of the opposite player
        
        """
        make a state of the future board using the new grid given.
        if the players king is exposed by new state legal moves, return False
        if the players king is not, then it is a legal move, return True
        call this function in a loop of all the legal moves that can be made by the piece
        """
        x, y = king.pos
        # inshaallah this works
        if grid[y][x][1] != 'k': 
            # print('false', self.grid[x][y], (x, y))
            return False  # two kings will never have the opportunity to capture each other. but if theres a bug in my code with kings involved, then ill know where to look
        else: 
            king = squares[y][x]
            # print(king)

        # [print(i) for i in squares]
        # print(player_pieces_list)
        # print(enemy_pieces_list)
        # print(f'\nKING: {king}')
        # print('PLAYERS LIST IN LEGAL POSITION METHOD:')
        # [print(i) for i in player_pieces_list];print('\n\n')
        
        # assert king is not None  # this might fix some bullshit  # this doesnt fix any bullshit  # it now exists as a relic of my stupidity
        
        # this should not run since we have access to the enemy moves list
        
        # print("ENEMY MOVES IS NONE AT IS_LEGAL_POSITION() METHOD")
        enemy_moves_unculled = []
        for piece in enemy_pieces_list:
            moves, _ = piece.valid_moves(squares, norecursion=True)
            [enemy_moves_unculled.append(move) for move in moves]
                
        # check if king is in the enemies move list
        # print('\nENEMY MOVES:')
        # [print(i) for i in self.enemy_moves_unculled]
        # print(king in self.enemy_moves_unculled)
        if king in enemy_moves_unculled:
            return False
        
        return True

    def check_castling(self, squares, short=False, longue=False):  # short, false will both

        """
        can probably be more optimized with special index magic stuff
        idk how bitboards can help here
        """

        enemy_moves = []

        if self.white_turn:

            enemy_moves = self.black_moves_unculled

            # king or both rooks have moved
            if not self.white_castling_possible:
                return False

            if not self.is_legal_position(squares, self.grid, self.black_pieces, self.king):
                return False
            
            if short:
                if not self.king_castle_short_white:
                    return False

                if squares[7][5] in enemy_moves or squares[7][6] in enemy_moves:
                    return False
                
                if squares[7][5].piece is not None or squares[7][6].piece is not None:
                    return False
                
            elif longue:  # the word long was already taken  # hmm so turns out its actually okay to use it, but it can get distracting maybe since its red in colour
                if not self.king_castle_long_white:
                    return False

                if squares[7][3] in enemy_moves or squares[7][2] in enemy_moves:
                    return False
                
                if squares[7][3].piece is not None or squares[7][2].piece is not None or squares[7][1].piece is not None:
                    return False
                
        else:
            
            enemy_moves = self.white_moves_unculled
            
            if not self.black_castling_possible:
                return False

            if not self.is_legal_position(squares, self.grid, self.white_pieces, self.king):
                return False
            
            if short:
                if not self.king_castle_short_black:
                    return False

                if squares[0][5] in enemy_moves or squares[0][6] in enemy_moves:
                    return False
                
                if squares[0][5].piece is not None or squares[0][6].piece is not None:
                    return False
                
            elif longue:
                if not self.king_castle_long_black:
                    return False

                if squares[0][3] in enemy_moves or squares[0][2] in enemy_moves:
                    return False
                
                if squares[0][3].piece is not None or squares[0][2].piece is not None or squares[0][1].piece is not None:
                    return False

        return True

    def new_move(self, GRID, origin, target, piece, checking_enpassant=False, checking_castling=False, promotion=False):

        """
        make a sim function: get pos of pieces if a move was to be made,
        if king is still attacked, return false. do this in the in_check method

        if this is run by each piece, the logic for clicking different squares could be much
        simpler. what would need to change are the flags here. each move could be tested against the is_legal_position()
        method.
        castling would probably be done the same by checking the flags here, but instead they would be
        computed in the kings legal move thing
        """

        new_grid = []

        # basically a more retarded deepcopy
        for row in GRID:
            new_row = []
            for sq in row:
                new_row.append(sq + '0')
            new_grid.append(new_row)

        x1, y1 = origin
        x2, y2 = target

        if checking_castling:  # this does not run if the enemy king is simply checking its legal moves

            # the king has moved => castling is not possible
            if piece == 'wk':
                self.king_castle_long_white = self.king_castle_short_white = False
                self.white_castling_possible = False

            elif piece == 'bk':
                self.king_castle_long_black = self.king_castle_short_black = False
                self.black_castling_possible = False
            
            elif piece == 'wr':

                # if long
                if x1 == 0 and y1 == 7:
                    self.king_castle_long_white = False
                    

                # if short
                elif x1 == 7 and y1 == 7:
                    self.king_castle_short_white = False
            
            elif piece == 'br':

                # if long for black
                if x1 == 0 and y1 == 0:
                    self.king_castle_long_black = False

                # if short for black
                elif x1 == 7 and y1 == 0:
                    self.king_castle_short_black = False

            # if a piece was moved to the rook's home - can only happen if rook is getting captured or if the rook has already moved
            if x2 == 0 and y2 == 0:
                self.king_castle_long_black = False
                
            elif x2 == 0 and y2 == 7:
                self.king_castle_long_white = False
                
            elif x2 == 7 and y2 == 7:
                self.king_castle_short_white = False
                
            elif x2 == 7 and y2 == 0:
                self.king_castle_short_black = False
                
        
        # check for enpassant
        if checking_enpassant:  # enpassant pawn is getting changed so I need to make a function that remembers the pawn that moved and save it after the new move has been created
            # print(f'CHECKING ENPASSANT - WHITE\'S TURN?: {self.white_turn}:\n\n')
            # clear all previous enpassant booleans if the player has not acted on it
            if self.white_turn:
                for enemy_piece in self.black_pieces:
                    if enemy_piece.class_value == 'pawn':
                        # print(all_pieces)
                        if self.move_number % 1 == 0:  # int % 1 is always 0, but int + 0.5 --> 0.5
                            # print(f'CLEARING BLACK PAWN: {enemy_piece}\n')
                            enemy_piece.enpassant = False  # maybe check by move number? this may be redundant after i change the pawn thing, since they all get cleared anyways
                            self.enpassant_pawn = None
                
                # check to see if enpassant is legal
                if piece == 'wp':  # redundant but who cares

                    if y1 == 6 and y2 == 4:
                        for piece_but_different in self.white_pieces:
                            if piece_but_different.yx_pos == (y1, x1) and piece_but_different.class_value == 'pawn':
                                self.enpassant_pawn = (x2, y2)

                                # print(f'SETTING NEW PAWN FOR WHITE: {self.enpassant_pawn}')
                                # print(f'\n{self.enpassant_pawn}\n')
                                piece_but_different.enpassant = True
                                break
                               

            elif not self.white_turn:
                for enemy_piece in self.white_pieces:
                    if enemy_piece.class_value == 'pawn':
                        if self.move_number % 1 == 0.5:
                            # print(f'CLEARING WHITE PAWN: {enemy_piece}\n')
                            enemy_piece.enpassant = False
                            self.enpassant_pawn = None

                if piece == 'bp':
                    if y1 == 1 and y2 == 3:
                        for piece_but_different in self.black_pieces:
                            if piece_but_different.yx_pos == (y1, x1) and piece_but_different.class_value == 'pawn':
                                self.enpassant_pawn = (x2, y2)

                                # print(f'SETTING NEW PAWN FOR BLACK: {self.enpassant_pawn}')
                                # print(f'\n{self.enpassant_pawn}\n')
                                piece_but_different.enpassant = True
                                break

        # for promotions, i know this can maybe be put under the enpassant flag for pawns but i LITERALLY dont give a shit
        if promotion:

            # these should not run when a bot is playing since the promotion decision is made before this method is called                
            if self.white_turn and piece == 'wp':
                if y2 == 0:
                    piece = self.game.promotion(x2, white=True)

            elif not self.white_turn and piece == 'bp':
                if y2 == 7:
                    piece = self.game.promotion(x2, black=True)

        # for enpassant    
        if self.white_turn:
            if piece == 'wp':
                # if enpassant has been played as white
                if y1 == 3 and y2 == 2:

                    if x2 == x1 - 1 and new_grid[y2][x1 - 1] == '000':
                        new_grid[y1][x1 - 1] = '000'

                    elif x2 == x1 + 1 and new_grid[y2][x1 + 1] == '000':
                        new_grid[y1][x1 + 1] = '000'
        
        elif not self.white_turn:
            if piece == 'bp':
                # if enpassant has been played as black
                if y1 == 4 and y2 == 5:
                    
                    if x2 == x1 - 1 and new_grid[y2][x1 - 1] == '000':
                        new_grid[y1][x1 - 1] = '000'

                    elif x2 == x1 + 1 and new_grid[y2][x1 + 1] == '000':
                        new_grid[y1][x1 + 1] = '000'

        new_grid[y1][x1] = '000'
        new_grid[y2][x2] = piece + '0'

        # do castling execution here
        if checking_castling:
            if piece == 'wk':
                if x1 == 4 and y1 == 7:
                    if x2 == 6 and y2 == 7:  # castled short for white
                        self.king_castle_short_white = False
                        self.king_castle_long_white = False

                        new_grid[7][7] = '000'
                        new_grid[7][5] = 'wr0'

                        self.white_castling_possible = False

                    elif x2 == 2 and y2 == 7:  # castled long for white
                        self.king_castle_long_white = False
                        self.king_castle_short_white = False

                        new_grid[7][0] = '000'
                        new_grid[7][3] = 'wr0'

                        self.white_castling_possible = False

            elif piece == 'bk':
                if x1 == 4 and y1 == 0:
                    if x2 == 6 and y2 == 0:  # castled short for black
                        self.king_castle_short_black = False
                        self.king_castle_long_black = False

                        new_grid[0][7] = '000'
                        new_grid[0][5] = 'br0'

                        self.black_castling_possible = False

                    elif x2 == 2 and y2 == 0:  # castled long for black
                        self.king_castle_long_black = False
                        self.king_castle_short_black = False

                        new_grid[0][0] = '000'
                        new_grid[0][3] = 'br0'

                        self.black_castling_possible = False

        returning_grid = []
        for new_row in new_grid:
            new_new_row = []
            for new_sq in new_row:
                new_new_row.append(new_sq[:2])
            returning_grid.append(new_new_row)

        return returning_grid

class ChessEngine:

    """
    This is going to be heavily rewritten:

    instead of searching for moves here, this class is going to
    focus solely on evaluating positions. The minimax algorithm 
    will be run here, but all evaluations will be static. this means
    that the bot will simply take in a position, it will create future
    positions based on all possible legal moves (the children), then
    it will evaluate the terminal nodes. the evaluation is where this
    class gets most-heavily applied.
    """

    def __init__(self, game, colour) -> None:
        self.game = game
        self.colour = colour  # i am not sure yet if i am going to use this attribute

        # these values will influence which moves the computer will prioritize
        self.white_pawn_positions = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [6, 6, 7, 7, 7, 7, 6, 6],
            [4, 4, 4, 4, 4, 4, 4, 4],
            [4, 4, 4, 4, 4, 4, 4, 4],
            [3, 3, 4, 4, 4, 4, 3, 3],
            [2, 2, 3, 3, 3, 3, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        self.black_pawn_positions = self.white_pawn_positions[::-1]  # reverse list gets the job done

        self.white_king_positions_opening = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 5, 4, 2, 2, 2, 4, 4]
        ]

        self.black_king_positions_opening = self.white_king_positions_opening[::-1]

        self.white_king_positions_endgame = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 4, 4, 4, 4, 2, 1],
            [1, 2, 4, 4, 4, 4, 2, 1],
            [1, 2, 4, 4, 4, 4, 2, 1],
            [1, 2, 4, 4, 4, 4, 2, 1],
            [1, 2, 2, 3, 3, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ]

        self.black_king_positions_endgame = self.white_king_positions_endgame[::-1]

        # think of this like the max power number in lethal company. if the sum of the enemy piece values are less than this number, the king will switch to the endgame's value
        self.opening_to_endgame_threshold = 15
        self.positions_searched = 0

        # these variables will be changed if the count dips below the endgame threshold
        self.white_king_current_map = self.white_king_positions_opening
        self.black_king_current_map = self.black_king_positions_opening

        self.knight_positions = [
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 3, 3, 3, 3, 3, 3, 1],
            [1, 3, 4, 4, 4, 4, 3, 1],
            [1, 3, 4, 5, 5, 4, 3, 1],
            [1, 3, 4, 5, 5, 4, 3, 1],
            [1, 3, 4, 4, 4, 4, 3, 1],
            [1, 3, 3, 3, 3, 3, 3, 1],
            [0, 1, 1, 1, 1, 1, 1, 0]
        ]

        self.bishop_positions = [
            [3, 1, 2, 2, 2, 2, 1, 3],
            [1, 4, 3, 3, 3, 3, 4, 1],
            [2, 3, 4, 2, 2, 4, 3, 2],
            [2, 3, 2, 4, 4, 2, 3, 2],
            [2, 3, 2, 4, 4, 2, 3, 2],
            [2, 3, 4, 2, 2, 4, 3, 2],
            [1, 4, 3, 3, 3, 3, 4, 1],
            [3, 1, 2, 2, 2, 2, 1, 3]
        ]

        self.rook_positions = [
            [1, 1, 1, 3, 3, 1, 1, 1],
            [1, 2, 2, 3, 3, 2, 2, 1],
            [1, 2, 2, 3, 3, 2, 2, 1],
            [2, 2, 3, 4, 4, 3, 2, 2],
            [2, 2, 3, 4, 4, 3, 2, 2],
            [1, 2, 2, 3, 3, 2, 2, 1],
            [1, 2, 2, 3, 3, 2, 2, 1],
            [1, 1, 1, 3, 3, 1, 1, 1]
        ]

        # this is just the average between the bishop and rook moves with minor adjustments lol
        self.queen_positions = [
            [2, 1, 2, 2, 2, 2, 1, 2],
            [1, 3, 2, 2, 2, 2, 3, 1],
            [2, 2, 3, 3, 3, 3, 2, 2],
            [2, 3, 3, 4, 4, 3, 3, 2],
            [2, 3, 3, 4, 4, 3, 3, 2],
            [2, 2, 3, 3, 3, 3, 2, 2],
            [1, 3, 2, 2, 2, 2, 3, 1],
            [2, 1, 2, 2, 2, 2, 1, 2]
        ]

        # completely arbitrary values
        self.piece_activity_factors = {
            'queen':  1.4,
            'king':   0.8,
            'pawn':   0.5,
            'rook':   1.2,
            'bishop': 1.2,
            'knight': 1.2
        }

        self.debug_checkmate_list = [
            [
            ['br', 'bn', 'bb', '00', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', '00', 'bp', 'bp', 'bp'],
            ['00', '00', '00', '00', 'bp', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', 'wp', 'bq'],
            ['00', '00', '00', '00', '00', 'wp', '00', '00'],
            ['wp', 'wp', 'wp', 'wp', 'wp', '00', '00', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
            ],

            [
            ['br', 'bn', 'bb', '00', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', '00', 'bp', 'bp', 'bp'],
            ['00', '00', '00', '00', 'bp', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', 'wp', 'wp', 'bq'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['wp', 'wp', 'wp', 'wp', 'wp', '00', '00', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
            ],

            [
            ['br', 'bn', 'bb', '00', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', '00', 'bp', 'bp', 'bp'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', 'bp', '00', '00', '00'],
            ['00', '00', '00', '00', '00', 'wp', 'wp', 'bq'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['wp', 'wp', 'wp', 'wp', 'wp', '00', '00', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
            ],

            [
            ['br', 'bn', 'bb', '00', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', '00', 'bp', 'bp', 'bp'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', 'bp', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', 'wp', 'bq'],
            ['00', '00', '00', '00', '00', 'wp', '00', '00'],
            ['wp', 'wp', 'wp', 'wp', 'wp', '00', '00', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
            ]
        ]

    def testing(self, pos):
        return 0
    
    def perft(self, white_turn, position, depth, count):
        if depth == 1:
            return len(position.children)

        elif depth > 1:
            for child in list(position.children.values()):
                piece_id = child[0]
                move = child[1]
                oy, ox = move[0]
                ty, tx = move[1]
                
                if white_turn:
                    castling_possible = position.white_castling_possible
                    castling_long = position.king_castle_long_white
                    castling_short = position.king_castle_short_white

                    king = position.white_king

                    new_grid, castling_possible, castling_long, castling_short, enpassant_pawn, king = new_move(position.grid, (oy, ox), (ty, tx), piece_id, position.enpassant_pawn, castling_possible, castling_long, castling_short, king, checking_enpassant=True, checking_castling=True)

                    new_position = Position_V2(move, not white_turn, new_grid, castling_long, position.king_castle_long_black, position.king_castle_short_black, castling_short, castling_possible, position.black_castling_possible, enpassant_pawn, king, position.black_king)
                    
                    count += self.perft(not white_turn, new_position, depth - 1, count)

                else:
                    castling_possible = position.black_castling_possible
                    castling_long = position.king_castle_long_black
                    castling_short = position.king_castle_short_black

                    king = position.black_king
                    
                    new_grid, castling_possible, castling_long, castling_short, enpassant_pawn, king = new_move(position.grid, (oy, ox), (ty, tx), piece_id, position.enpassant_pawn, castling_possible, castling_long, castling_short, king, checking_enpassant=True, checking_castling=True)
                
                    new_position = Position_V2(move, not white_turn, new_grid, position.king_castle_long_white, castling_long, castling_short, position.king_castle_short_white, position.white_castling_possible, castling_possible, enpassant_pawn, position.white_king, king)

                    count += self.perft(not white_turn, new_position, depth - 1, count)
        else:
            print('if we get here, then we\'re fucked')
            return 1

    def minimax(self, position, max_player: bool, alpha, beta, depth):

        """
        instead, this will actually be the minmaxing function.
        it will be recursive, taking five parameters: board, depth, 
        white (maxxing player), alpha (initialized to -inf), and 
        beta (initialized to +inf).

        for testing, let depth be 5. then, every possible position
        will be created up to a depth of 5 - could be hundreds of
        positions [it ended up being 4 897 256 positions]. each 
        terminal position will be evaluated and a float will be 
        assigned to it. < 0 is best for black, > 0 is best for 
        white. at the same time, we choose an alpha and beta based
        on the max of the eval and the alpha, and the min of the eval
        and the beta, respectively. essentially, if, in the same branch, 
        a better move exists than the currently-evaluated position, then
        the other moves in that position will not be evaluated. we can
        trust this, as the player will always choose its best-case
        position. once a terminal node is reached, we update the eval
        of the position and compare it against the max eval, updating
        if necessary. this process is repeated until there are no more
        relevant nodes to search. then, the move that led to the 
        best-case scenario is played. note, only the first move in
        the move order is returned. perhaps after testing, the move order
        itself may be returned, though this can only provide worse moves
        as new depths are not considered.
        """

        if depth == 0 or position.checkmate() != 0:

            self.game.different_positions_grid[self.game.positions_searched] = position.grid
            self.game.positions_searched += 1
            print(self.game.positions_searched)

            return self.testing(position)
        
        # maximizing player
        if max_player:
            max_eval = -1e50
            for child in position.children:
                current_child = position.children[child]
                
                y, x = current_child[1][0]  # origin
                move_pos = current_child[1][1]  # target
                piece_id = current_child[0]  # id

                new_grid, castling_possible, castle_long, castle_short, enpassant_pawn, king = new_move(position.grid, (y, x), move_pos, piece_id, position.enpassant_pawn, position.white_castling_possible, position.king_castle_long_white, position.king_castle_short_white, position.king, checking_castling=True, checking_enpassant=True)
                
                new_position = Position_V2(current_child, False, new_grid, castle_long, position.king_castle_long_black, position.king_castle_short_black, castle_short, castling_possible, position.black_castling_possible, enpassant_pawn, king, position.black_king)
                
                evaluation = self.minimax(new_position, False, alpha, beta, depth - 1)
                max_eval = max(evaluation, max_eval)
                # alpha = max(evaluation, alpha)
                # if beta <= alpha:
                #     break
            return max_eval
        
        # minimizing player
        else:
            min_eval = 1e50
            for child in position.children:
                current_child = position.children[child]
                
                y, x = current_child[1][0]  # origin
                move_pos = current_child[1][1]  # target
                piece_id = current_child[0]  # id

                new_grid, castling_possible, castle_long, castle_short, enpassant_pawn, king = new_move(position.grid, (y, x), move_pos, piece_id, position.enpassant_pawn, position.black_castling_possible, position.king_castle_long_black, position.king_castle_short_black, position.king, checking_castling=True, checking_enpassant=True)
                
                new_position = Position_V2(current_child, True, new_grid, position.king_castle_long_white, castle_long, castle_short, position.king_castle_short_white, position.white_castling_possible, castling_possible, enpassant_pawn, position.white_king, king)
                
                evaluation = self.minimax(new_position, True, alpha, beta, depth - 1)
                min_eval = min(evaluation, min_eval)
                # beta = min(evaluation, beta)
                # if beta <= alpha:
                #     break
            return min_eval

    def get_piece_activity_score(self, board, player_pieces, enemy_pieces):
        """
        returns int scores for each piece - different scores based on piece type.
        stronger weight to enemy pieces as it is generally not great for a player
        to play a move that gives the enemy way more activity
        """
        white_score = black_score = 0

        for piece in player_pieces:
            moves = piece.valid_moves(board, cull_illegal_moves=True)
            factor = self.piece_activity_factors[piece.class_value]
            score = len(moves) * factor
            if piece.colour == 'w':
                white_score += score
            else:
                black_score += score
        
        for piece in enemy_pieces:
            moves = piece.valid_moves(board, cull_illegal_moves=True)
            factor = self.piece_activity_factors[piece.class_value]
            score = len(moves) * factor
            if piece.colour == 'w':
                white_score += score
            else:
                black_score += score

        return white_score, black_score

    def apply_piece_map(self, board, white_pieces, black_pieces, scale=1):
        """
        I am not sure which arguments i will need here.
        this will scale and apply the values of the 
        appropriate value map to the grade of the evaluate
        method.

        for now, i will test this by dividing all values by 2,
        regardless of the type of piece. scale is changed when the
        method is called
        """
        positional_worth_white = positional_worth_black = 0
        for piece in white_pieces:
            i, j = piece.x // self.game.Xtl, piece.y // self.game.Ytl
            if piece.class_value == 'queen':
                position_value = self.queen_positions[j][i] * scale

            elif piece.class_value == 'pawn':
                position_value = self.white_pawn_positions[j][i] * scale

            elif piece.class_value == 'rook':
                position_value = self.rook_positions[j][i] * scale

            elif piece.class_value == 'knight':
                position_value = self.knight_positions[j][i] * scale

            elif piece.class_value == 'bishop':
                position_value = self.bishop_positions[j][i] * scale

            elif piece.class_value == 'king':
                _, black_score = self.get_player_scores(board)

                if black_score <= self.opening_to_endgame_threshold:
                    king_position_map = self.white_king_positions_endgame
                else:
                    king_position_map = self.white_king_positions_opening

                position_value = king_position_map[j][i] * scale
            
            positional_worth_white += position_value

        for piece in black_pieces:
            i, j = piece.x // self.game.Xtl, piece.y // self.game.Ytl
            if piece.class_value == 'queen':
                position_value = self.queen_positions[j][i] * scale

            elif piece.class_value == 'pawn':
                position_value = self.black_pawn_positions[j][i] * scale

            elif piece.class_value == 'rook':
                position_value = self.rook_positions[j][i] * scale

            elif piece.class_value == 'knight':
                position_value = self.knight_positions[j][i] * scale

            elif piece.class_value == 'bishop':
                position_value = self.bishop_positions[j][i] * scale

            elif piece.class_value == 'king':
                white_score, _ = self.get_player_scores(board)

                if white_score <= self.opening_to_endgame_threshold:
                    king_position_map = self.black_king_positions_endgame
                else:
                    king_position_map = self.black_king_positions_opening

                position_value = king_position_map[j][i] * scale
            
            positional_worth_black += position_value

        return positional_worth_white, positional_worth_black

    def promotion_request(self, board, move):
        """
        Checks which of the options is best for the position (usually queen but you never know)


        this may not be necessary with the minimax algo - just need a way to get potential
        promotions
        """

        possibilities = [f'{self.colour}q', f'{self.colour}r', f'{self.colour}n', f'{self.colour}b']
        default = possibilities[0]
        # self.evaluate_position(board, move, ..., ..., ...)  # need to fix this up later. for now, autoqueen
        return default

    def get_player_scores(self, board):

        white_score = black_score = 0
        for row in board:
            for square in row:
                if square.piece is not None:
                    if square.piece.colour == 'w':
                        white_score += square.piece.worth * 2.1  # this is just an arbitrary thing ngl
                        # this can be improved upon by altering the values based on piece type - capturing a pawn is not as great as capturing a queen
                        
                    elif square.piece.colour == 'b':
                        black_score += square.piece.worth * 2.1  

        return white_score, black_score

    def evaluate_position(self, board, grid, move):
        """
        This method will be run on all available moves.

        perhaps the yield keyword might be of use here when the depth is implemented.

        currently, the "future" variables are slightly misleading, as
        all future positions are generated in the generate_move() method.
        should probably rename the variables to "current" state for better
        readability

        TODO: use the grid to simulate and store future positions in the children nodes.
        actually, may not need to do this - we simply need the legal moves of the position,
        and for those moves to be applied.

        TODO: rewrite this method to use the positions class instead of game class
        """

        origin_square = board[move[0].y // self.game.Ytl][move[0].x // self.game.Xtl]
        move_pos = move[1].pos

        grade = 0

        board_state = self.game.new_move(origin_square.pos, move_pos, origin_square.piece.id)  # maybe i can make a hidden flag for specific bot promotions
        black_pieces, white_pieces, squares_list = create_grid(self, board_state)  #TODO: make the "self" a position object instead

        pieces_list = (white_pieces, black_pieces) if self.colour == 'w' else (black_pieces, white_pieces)
        player_pieces = pieces_list[0]
        enemy_pieces = pieces_list[1]

        player_moves = []
        for piece in player_pieces:
            moves = piece.valid_moves(squares_list)
            [player_moves.append(move) for move in moves]

        enemy_moves = []  #TODO: get king pos in this loop, do same for white to find if checkmate is on the board
        for piece in enemy_pieces:
            if piece.class_value == 'king':
                enemy_king = squares_list[piece.y // self.game.Ytl][piece.x // self.game.Xtl]

            moves = piece.valid_moves(squares_list, cull_illegal_moves=True)
            [enemy_moves.append(move) for move in moves]

        if enemy_moves == [] and enemy_king in player_moves:
            return "checkmate"

        white_score, black_score = self.get_player_scores(squares_list)  # it is faster to just use the new_move method to calculate the total, but it may be nicer to set it up so that i can check the position of already-simulated pieces
        
        white_position_value, black_position_value = self.apply_piece_map(squares_list, white_pieces, black_pieces, scale=1.5)
        white_score += white_position_value
        black_score += black_position_value

        white_activity_score, black_activity_score = self.get_piece_activity_score(squares_list, player_pieces, enemy_pieces)  # this can be optimized by doing this calcuation when we search for checkmate
        white_score += white_activity_score
        black_score += black_activity_score

        # for now, this method will only look at material gain.
        # depth will be used later to evaluate future moves in the position
        # as this method technically is being used to check moves with depth 1 anyways
        grade += white_score - black_score
        # grade *= random.randint(8, 12) / 10  # lolll, just a bit of randomness to spice things up a bit  # horrendous idea

        return grade

    def generate_move(self, board, white_pieces, black_pieces):
        """
        this method is only for testing, should be renamed so as to be less ambiguous

        "wahhw, u can really dance :o" - current state of the bot

        this needs to be rewritten with the minimax algorithm instead
        """
        
        if self.colour == 'w':
            moves_list = []
            for piece in white_pieces:
                if piece.class_value == 'king':
                    piece_moves = piece.valid_moves(board, cull_illegal_moves=True, add_castling=True)

                else:
                    piece_moves = piece.valid_moves(board, cull_illegal_moves=True)

                for move in piece_moves:
                    moves_list.append((piece, move))

            white_score, black_score = self.get_player_scores(board)
            best_gain = white_score - black_score
            best_move = random.choice(moves_list)  # if there is no better move, the computer will just play an random move for now - wil probably never be used later on when positions are taken into account
            
            for move in moves_list:
                gain = self.evaluate_position(board, move)
                if gain == 'checkmate':
                    best_move = move
                    break
                if gain > best_gain:
                    best_gain = gain
                    best_move = move

        elif self.colour == 'b':
            moves_list = []
            for piece in black_pieces:
                if piece.class_value == 'king':
                    piece_moves = piece.valid_moves(board, cull_illegal_moves=True, add_castling=True)

                else:
                    piece_moves = piece.valid_moves(board, cull_illegal_moves=True)

                for move in piece_moves:
                    moves_list.append((piece, move))

            white_score, black_score = self.get_player_scores(board)
            best_gain = white_score - black_score
            best_move = random.choice(moves_list)
            
            for move in moves_list:
                gain = self.evaluate_position(board, move)
                if gain == 'checkmate':
                    best_move = move
                    break

                elif gain < best_gain:
                    best_gain = gain
                    best_move = move

        piece = best_move[0]
        move = best_move[1]

        origin_square = board[piece.y //self.game.Ytl][piece.x // self.game.Xtl]
        piece_id = piece.id

        # this unfortunately will not currently take into account the future benefits of promoting as it takes place after a move is chosen
        if piece.id == 'wp':
            if move.pos[1] == 0:
                piece_id = self.promotion_request(False, False)  # placeholder variables

        if piece.id == 'bp':
            if move.pos[1] == 7:
                piece_id = self.promotion_request(False, False)

        return (origin_square, move, piece_id)

