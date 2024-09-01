"""
This is meant to be a more optimized version of the position class.
many methods have been moved into the pieces_V2 library
"""

from pieces_V2 import *

class Square:
    def __init__(self, game, x, y, colour, pg):
        self.game = game
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl
        self.pygame = pg

        self.pos = (y, x)

        self.colour = self.game.cl[colour]
        self.normal_colour = self.colour
        self.clicked = False # square is clicked
        self.legal_move = False # highlight legal moves
        self.rect = self.pygame.Rect(self.x, self.y, self.game.Xtl, self.game.Ytl) # square rect, also used for collidepoint()
        self.piece = None # piece stored on square

        # used only for promotion instances. [image, id]
        self.graphic = None

    def __repr__(self):
        x = self.x // self.game.Xtl
        y = self.y // self.game.Ytl

        if self.piece == None:
            return f'E, {x, y}'
        return f'{self.piece.id, (x, y)}'

    def draw(self, default=True):
        
        self.pygame.draw.rect(self.game.display, self.colour, self.rect)

        if not default:
            # for some reason, its a list in a tuple lol
            # LMFAOOO its no longer a tuple and idk why
            self.game.display.blit(self.graphic[0], (self.x, self.y))

class Position_V2:

    """
    this is for the chess engine to use. each boardstate will be converted to
    a Position object that stores its legal moves, player to move, eval, and
    potentially, the move that was played to reach it (only if immediate child to
    the root node - we dont need all the moves to be stored).
    """

    def __init__(self, move, white_turn: bool, grid, king_castle_long_white, king_castle_long_black, king_castle_short_black, king_castle_short_white, white_castling_possible, black_castling_possible, enpassant_pawn, white_king, black_king ) -> None:
        
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

        self.white_turn = white_turn

        self.move_number = 0  # default value, gets changed otherwise
        
        self.move = move
        self.grid = grid  # to make new moves
        self.white_pieces, self.black_pieces = get_pieces_list(self.grid)

        # make a function that updates these values based on the position 
        # so that they can be stored when moves are simulated. ie, if in a 
        # branch, player decides to castle, they cannot castle later on in that same branch
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
                        self.white_king = (i, j)

                    if val == 'bk':
                        self.black_king = (i, j)
                    
        else:
            self.white_king = white_king
            self.black_king = black_king

        if self.white_turn:
            self.king = self.white_king
            self.player_pieces = self.white_pieces
            self.enemy_pieces = self.black_pieces

            castling_possible = self.white_castling_possible
            castling_long = self.king_castle_long_white
            castling_short = self.king_castle_short_white

        else:
            self.king = self.black_king
            self.player_pieces = self.black_pieces
            self.enemy_pieces = self.white_pieces

            castling_possible = self.black_castling_possible
            castling_long = self.king_castle_long_black
            castling_short = self.king_castle_short_black

        # initialize the move lists
        self.player_moves = []
        # self.enemy_moves = []
        # self.player_moves_unculled = []
        self.enemy_moves_unculled = []

        king_col = self.grid[self.king[0]][self.king[1]][0]
        for i, row in enumerate(self.grid):
            for j, col in enumerate(row):
                if col[0] != king_col and col != '00':
                    all_moves = match_piece_moves(col[1], col[0], (i, j), self.grid, self.enpassant_pawn, None, False, False, False, castling=False)
                    for move in all_moves[1]:
                        
                        self.enemy_moves_unculled.append(move)

        self.children = {}
        
        # idk, ill optimize it later with bitboards or something
        # print('\ntime needed to make children')
        # t = time.time()

        for i, row in enumerate(self.grid):
            for j, col in enumerate(row):
                
                if col[0] == king_col:
                    is_promoting = False
                    k = len(self.children)  # ensures no duplicates in the dict

                    # for promotions
                    if (col == 'wp' and i == 1) or (col == 'bp' and i == 6):
                        # print(f'\nTime needed to generate moves and promotion: {piece}')
                        # t = time.time()
                        future_moves = match_piece_moves(col[1], col[0], (i, j), self.grid, self.enpassant_pawn, self.enemy_moves_unculled, False, False, False, castling=False)
                        
                        bad_moves = illegal_moves(self.king, self.grid, future_moves)
                        for move in bad_moves:
                            
                            future_moves[1].remove(move[1])

                        # for move in future_moves[1]:
                        #     self.player_moves.append(move)
                        
                        moves = self.promotion(col[0], future_moves)
                        is_promoting = True
                        # print(time.time() - t)

                    else:
                        print(castling_short)
                        moves = match_piece_moves(col[1], col[0], (i, j), self.grid, self.enpassant_pawn, self.enemy_moves_unculled, castling_possible, castling_long, castling_short, castling=True)
                        # pos, all_moves
                     
                        bad_moves = illegal_moves(self.king, self.grid, moves)
                     
                        # print(moves, bad_moves)
                        for move in bad_moves:
                            # move is (origin, move)
                            moves[1].remove(move[1])
                       
                        
                        #TODO: idk if i need this loop, but if i do, its here
                        # for move in moves:
                        #     self.player_moves.append(move)
                        
                    # keep this dict simple so that the program isnt storing/generating like 80 objects each time
                    if not is_promoting:
                        for l, move in enumerate(moves[1]):
                            # print(moves[0])
                            # print(moves[1])
                            # print('\n')

                            # have an if flag here for promotion? probably
                            # idk if this is actually going to work but ig we'll see lol
                            
                            s = k + l
                            # print(move)
                            self.children[s] = (col, (moves[0], move))  # (piece id, (origin, target))
                        
                    else:
                        for l in range(len(moves)):

                            # TODO: fix this up for later
                            
                            s = k + l
                            # print(move[0], move[1])
                            
                            self.children[s] = moves[l]
                            
        pass
    
    def promotion(self, colour, moves):

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
        origin = moves[0]
        targets = moves[1]
        for move in targets:
            
            all_moves.append((f'{colour}q', (origin, move)))
            all_moves.append((f'{colour}r', (origin, move)))
            all_moves.append((f'{colour}n', (origin, move)))
            all_moves.append((f'{colour}b', (origin, move)))

        return all_moves

    def checkmate(self, check_insufficient_material=True):

        # checks for insufficient material
        if check_insufficient_material:
            if len(self.player_pieces) <= 2 and len(self.enemy_pieces) <= 2:
                # print(self.player_pieces, self.enemy_pieces)
                if len(self.player_pieces) == 1 and len(self.enemy_pieces) == 1:  # only kings on the board (or else something has gone very, very wrong)
                    return 3

                for pos in self.player_pieces:
                    
                    if pos != self.king:
                        other_piece = self.grid[pos[0]][pos[1]][1]

                for pos in self.enemy_pieces:
                    
                    if self.grid[pos[0]][pos[1]][1] != 'k':
                        enemy_other_piece = self.grid[pos[0]][pos[1]][1]

                # what a lazy solution!
                if (not len(self.player_pieces) == 1 and other_piece == 'n') or (not len(self.player_pieces) == 1 and other_piece == 'b'):
                    if len(self.enemy_pieces) == 1:  # only king
                        return 3
                    
                    if (not len(self.enemy_pieces) == 1 and enemy_other_piece == 'n') or (not len(self.enemy_pieces) == 1 and enemy_other_piece == 'b'):
                        return 3

        if len(self.children) == 0:
            
            if self.king in self.enemy_moves_unculled:  # checkmate

                
                return 1
            
            # else: stalemate
            return 2
        
        return 0