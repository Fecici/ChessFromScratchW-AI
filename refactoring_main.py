"""
most important thing right now is to modularize everything. what i need to figure out
is how the parameters should be accessed - by the game attributes or by passing special
arguments?


to add even a random move AI the AI needs to know which moves are even possible.
the best way to do this currently seems to move the check for legal moves into the
piece class valid_move() method. it would simply take in copies if the squares list and stuff
(so as to avoid the quantum chess bug). castling and enpassant would probably use the same
methods to compute, but maybe minor tweaks will need to be made in the piece move method.
promotions will also need to be kind of re-done to be bot-friendly. i also need to figure 
out how to make it play against itself, or even how to play as either black or white. should also
make it slightly delayed so that it doesnt instantly move. this can just be done by checking if 
delta-time is >= 1 or something

for custom positions, castling will simply need to make checks at the beginning of the game
before assigning the possibility of castling as True to the game attributes.
"""

import pygame; import math; import random; import time; import sys; from copy import deepcopy; from refactoring_pieces import King, Queen, Pawn, Bishop, Knight, Rook; from chessEngine import ChessEngine

outside_class_grid = [ # first letter is colour, second is piece in chess notation, 00 is empty
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
        ]

class Spritesheet:
    def __init__(self, file):
        try:
            self.file = pygame.image.load(file).convert_alpha()

        except FileNotFoundError:
            print('Error: File not detected')

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h)) # create empty surface
        sprite.blit(self.file, (0, 0), (x, y, w, h)) # blit image onto surface
        sprite.set_colorkey((0, 0, 0)) # creating an empty surface set the default colour to (0, 0, 0) for the space
        return sprite # return surface with the image blitted on it

class Square:
    def __init__(self, game, x, y, colour):
        self.game = game
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.pos = (self.x // self.game.Xtl, self.y // self.game.Ytl)

        self.colour = self.game.cl[colour]
        self.normal_colour = self.colour
        self.clicked = False # square is clicked
        self.legal_move = False # highlight legal moves

        self.rect = pygame.Rect(self.x, self.y, self.game.Xtl, self.game.Ytl) # square rect, also used for collidepoint()

        self.piece = None # piece stored on square

        # used only for promotion instances. [image, id]
        self.graphic = None

    def __repr__(self):
        x = self.x // self.game.Xtl
        y = self.y // self.game.Ytl

        if self.piece == None:
            return f'E, {x, y}'
        return f'{self.piece.id, x, y}'

    def draw(self, default=True):
        
        pygame.draw.rect(self.game.display, self.colour, self.rect)

        if not default:
            # for some reason, its a list in a tuple lol
            self.game.display.blit(self.graphic[0][0], (self.x, self.y))

class Game:
    def __init__(self):
        pygame.init()
        self.WINW, self.WINH = 1000, 1000

        self.Xtl = self.WINW//8
        self.Ytl = self.WINH//8

        self.display = pygame.display.set_mode((self.WINW, self.WINH))
        pygame.display.set_caption('Chess')

        self.cl = {
            'b': (0, 0, 0),
            'w': (255, 255, 255),
            'g': (128, 128,128),
            'dg': (96, 96, 96),
            'bg': (55, 117, 128)
        }

        self.clock = pygame.time.Clock()
        self.FPS = 600

        self.run = False
        self.spritesheet = Spritesheet('Chess\img\spritesheet.png')

        self.grid = outside_class_grid

        self.testing_grid = [  # TESTING ONLY
            ['wk', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', 'br', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', 'wr', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', 'bk'],
        ]

        self.GRID = self.grid.copy()

        self.squares = []  # contains all of the squares in the board

        self.white_pieces = []
        self.black_pieces = []

        self.squares_to_move = []  # these are all legal moves that the selected piece can move
        self.selected_square = None  # the selected square
        self.enpassant_pawn = None

        # debug
        self.debug_checkmate = False

        # different cases for the board
        self.king_castle_long_white = self.king_castle_long_black = self.king_castle_short_black = self.king_castle_short_white = True  # this will be reused - checks if either side is possible, is different from the other variable as it checks if the rooks have moved, not the king
        self.rook_castle_long_white = self.rook_castle_long_black = self.rook_castle_short_black = self.rook_castle_short_white = True  # no longer in use
        self.white_castling_possible = self.black_castling_possible = True

        self.white_turn = True
        self.move_number = 0
        self.game_states = {}  # could write to json file? each state could have its info stored in json for ease of access. this could just be a regular dict that stores all the relevant gamestate attributes

        # AI stuff
        self.white_AI = True
        self.black_AI = True

        self.white_bot = None
        self.black_bot = None

        if not self.white_AI and not self.black_AI:
            self.is_humans_turn = True

        if self.white_AI:
            self.is_humans_turn = False
        
        elif self.black_AI:
            if not self.white_AI:
                self.is_humans_turn = True
            else:
                self.is_humans_turn = False

    def mk_pieces(self, piece, x, y):
        resulting_piece = None

        if piece == 'br':
            resulting_piece = Rook(self, x, y, piece[0], piece)

        if piece == 'bn':
            resulting_piece = Knight(self, x, y, piece[0], piece)

        if piece == 'bb':
            resulting_piece = Bishop(self, x, y, piece[0], piece)

        if piece == 'bq':
            resulting_piece = Queen(self, x, y, piece[0], piece)

        if piece == 'bk':
            resulting_piece = King(self, x, y, piece[0], piece)

        if piece == 'bp':
            resulting_piece = Pawn(self, x, y, piece[0], piece)

        if piece == 'wp':
            resulting_piece = Pawn(self, x, y, piece[0], piece)

        if piece == 'wr':
            resulting_piece = Rook(self, x, y, piece[0], piece)

        if piece == 'wn':
            resulting_piece = Knight(self, x, y, piece[0], piece)

        if piece == 'wb':
            resulting_piece = Bishop(self, x, y, piece[0], piece)

        if piece == 'wq':
            resulting_piece = Queen(self, x, y, piece[0], piece)

        if piece == 'wk':
            resulting_piece = King(self, x, y, piece[0], piece)

        return resulting_piece


    def create_grid(self, grid):

        black_pieces = []
        white_pieces = []

        squares = []
        for i, row in enumerate(grid):  # tile map technique
            a = []  # 'a' is just another list that makes it so the resulting multidimentional list has a de facto x and y value
            for j, col in enumerate(row):
                if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):  # this condition makes the black-white pattern
                    square = Square(self, j, i, 'w')
                    a.append(square)

                else:
                    square = Square(self, j, i, 'g')
                    a.append(square)

                new_piece = self.mk_pieces(col, j, i)  # value, x, y
                if new_piece != None:

                    square.piece = new_piece

                    if new_piece.colour == 'w':
                        white_pieces.append(new_piece)

                    else:
                        black_pieces.append(new_piece)

            squares.append(a) # squares is a 2 dimensional list

        return black_pieces, white_pieces, squares
    
    def promotion(self, x, white=False, black=False):
        
        promotion_run = True
        promoted_piece = False  # if this remains false until after the while loop, something has gone very wrong

        # this could have just gone to the __init__() method but who fuckin cares lol
        white_sprites = [
            [self.spritesheet.get_sprite(120 * 10, 0, self.Xtl, self.Ytl), 'wq'], 
            [self.spritesheet.get_sprite(120 * 11, 0, self.Xtl, self.Ytl), 'wr'], 
            [self.spritesheet.get_sprite(120 * 8,  0, self.Xtl, self.Ytl), 'wn'], 
            [self.spritesheet.get_sprite(120 * 6,  0, self.Xtl, self.Ytl), 'wb']         
            ]
        
        black_sprites = [
            [self.spritesheet.get_sprite(120 * 4,  0, self.Xtl, self.Ytl), 'bq'], 
            [self.spritesheet.get_sprite(120 * 5,  0, self.Xtl, self.Ytl), 'br'], 
            [self.spritesheet.get_sprite(120 * 2,  0, self.Xtl, self.Ytl), 'bn'], 
            [self.spritesheet.get_sprite(120 * 0,  0, self.Xtl, self.Ytl), 'bb']         
            ]
        
        promotion_squares = []

        if white: sprites = white_sprites
        elif black: sprites = black_sprites[::-1]  # reverse because it looks nicer

        c = 0 if white else 4  # just a magic number to help fix the y pos for black

        for i in range(4):
            promotion_square = Square(self, x, i + c, 'w')
            promotion_square.graphic = sprites[i],
            promotion_squares.append(promotion_square)

        while promotion_run:
            if self.white_turn and self.white_AI:
                promoted_piece = random.choice(promotion_squares).graphic[0][1]
                promotion_run = False
                break

            elif not self.white_turn and self.black_AI:
                promoted_piece = random.choice(promotion_squares).graphic[0][1]
                promotion_run = False
                break
            
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    for square in promotion_squares:
                        if square.rect.collidepoint(pos):
                            promoted_piece = square.graphic[0][1]
                            promotion_run = False

            for square in promotion_squares:
                square.draw(default=False)
            pygame.display.update()
        return promoted_piece


    def new_move(self, origin, target, piece, checking_enpassant=False, checking_castling=False, promotion=False):

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

        for row in self.GRID:
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
                for item in self.white_pieces:

                    # checks if the rook is the currently selected one
                    if item.x // self.Xtl == x1 and item.y // self.Ytl == y1 and item.class_value == 'rook':  # the last flag should never return False, but again, im fukcing paranoid man
                        
                        # if long
                        if x1 == 0 and y1 == 7:
                            self.king_castle_long_white = False
                            break
                            

                        # if short
                        elif x1 == 7 and y1 == 7:
                            self.king_castle_short_white = False
                            break
                            
            
            elif piece == 'br':
                for item in self.black_pieces:

                    if item.x // self.Xtl == x1 and item.y // self.Ytl == y1 and item.class_value == 'rook':  # see above

                        # if long for black
                        if x1 == 0 and y1 == 0:
                            self.king_castle_long_black = False
                            break

                        # if short for black
                        elif x1 == 7 and y1 == 0:
                            self.king_castle_short_black = False
                            break

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
            
            # clear all previous enpassant booleans if the player has not acted on it
            if self.white_turn:
                for all_pieces in self.white_pieces:
                    if all_pieces.class_value == 'pawn':
                        # print(all_pieces)
                        if self.move_number % 1 == 0:
                            all_pieces.enpassant = False  # maybe check by move number? this may be redundant after i change the pawn thing, since they all get cleared anyways
                            self.enpassant_pawn = None
                
                # check to see if enpassant is legal
                if piece == 'wp':  # redundant but who cares

                    if y1 == 6 and y2 == 4:
                        for piece_but_different in self.white_pieces:
                            if piece_but_different.x // self.Xtl == x1 and piece_but_different.y // self.Ytl == y1 and piece_but_different.class_value == 'pawn':
                                self.enpassant_pawn = (x2, y2)
                                piece_but_different.enpassant = True
                               

            elif not self.white_turn:
                for all_pieces in self.black_pieces:
                    if all_pieces.class_value == 'pawn':
                        if self.move_number % 1 == 0.5:

                            all_pieces.enpassant = False
                            self.enpassant_pawn = None

                if piece == 'bp':
                    if y1 == 1 and y2 == 3:
                        for piece_but_different in self.black_pieces:
                            if piece_but_different.x // self.Xtl == x1 and piece_but_different.y // self.Ytl == y1 and piece_but_different.class_value == 'pawn':
                                self.enpassant_pawn = (x2, y2)
                                piece_but_different.enpassant = True

        # for promotions, i know this can maybe be put under the enpassant flag for pawns but i LITERALLY dont give a shit
        if promotion:

            # these should not run when a bot is playing since the promotion decision is made before this method is called                
            if self.white_turn and piece == 'wp':
                if y2 == 0:
                    piece = self.promotion(x2, white=True)

            elif not self.white_turn and piece == 'bp':
                if y2 == 7:
                    piece = self.promotion(x2, black=True)

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

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                key_list = pygame.key.get_pressed()
                if key_list[pygame.K_LSHIFT] and key_list[pygame.K_p]:
                    for i in self.white_pieces:
                        if i.class_value == 'pawn':
                            print(f'{i}, {i.enpassant}')
                    print('\n\n')

                if key_list[pygame.K_LSHIFT] and key_list[pygame.K_o]:
                    for i in self.black_pieces:
                        if i.class_value == 'pawn':
                            print(f'{i}, {i.enpassant}')
                    print('\n\n')

                if key_list[pygame.K_LSHIFT] and key_list[pygame.K_w]:
                    print('\nWHITE PIECES:')
                    pass  # will make a switch for ai here or something maybe
                
                if key_list[pygame.K_LSHIFT] and key_list[pygame.K_b]:
                    print('\nBLACK PIECES:')
                    pass  # will make a switch for ai here or something maybe
                
                # if key_list[pygame.K_c]:
                #     self.debug_checkmate = not self.debug_checkmate

                if key_list[pygame.K_r]:
                    return True

            if event.type == pygame.MOUSEBUTTONDOWN and self.is_humans_turn: # test MOUSEBUTTONUP vs MOUSEBUTTONDOWN, main goal is to avoid unintentional spammed button clicks on squares

                pos = pygame.mouse.get_pos()

                for row in self.squares:
                    for square in row:
                        if square.rect.collidepoint(pos):
                            selected_square = square
                            
                # if i click on a different square that isnt in the move list
                if selected_square != self.selected_square and selected_square not in self.squares_to_move:
                    if self.selected_square != None: self.selected_square.clicked = False
                    selected_square.clicked = True

                    for lines_persisting in self.squares_to_move: # if i forget why this iter name is funny, just ask jodran
                        lines_persisting.clicked = False
                        lines_persisting.legal_move = False

                    self.squares_to_move = []
                    self.selected_square = selected_square
                    
                    # if a piece is on the selected square
                    if self.selected_square.piece != None:
                    
                        if self.check_colour_turn(self.selected_square.piece):  # ensures the correct colour is playing

                            if self.selected_square.piece.class_value == 'king':
                                self.squares_to_move = self.selected_square.piece.valid_moves(self.squares, cull_illegal_moves=True, add_castling=True)

                            else:
                                self.squares_to_move = self.selected_square.piece.valid_moves(self.squares, cull_illegal_moves=True)

                            for s in self.squares_to_move:  # highlight the legal moves
                                s.legal_move = True
                
                # if the selected square isn't itself and it is a legal move (a move has been played)
                elif selected_square != self.selected_square and selected_square.legal_move:

                    # updates the game state; the conditional only applies for checkmate/stalemate
                    if self.new_game_state(self.selected_square, selected_square, self.selected_square.piece.id):
                        return True

                # if i click on the same square
                elif selected_square == self.selected_square:
                    selected_square.clicked = False

                    for lines_persisting in self.squares_to_move: # if i forget why this iter name is funny, just ask jodran
                        lines_persisting.clicked = False
                        lines_persisting.legal_move = False
                    self.squares_to_move = []
                    self.selected_square = None

    def illegal_moves(self, potential_moves, selected_square):

        bad = []  # list of illegal moves
        for move in potential_moves:  # 'move' is a Square object here

            future_state = self.new_move(selected_square.pos, move.pos, selected_square.piece.id)
            future_black_pieces, future_white_pieces, future_squares_list = self.create_grid(future_state)

            # choose pieces list based on turn
            opposite_pieces_list = future_black_pieces if self.white_turn else future_white_pieces
            if self.white_turn:
                opposite_pieces_list = future_black_pieces
                player_pieces_list = future_white_pieces
            else:
                opposite_pieces_list = future_white_pieces
                player_pieces_list = future_black_pieces
            
            # check each position
            if not self.is_legal_position(future_squares_list, player_pieces_list, opposite_pieces_list):
                bad.append(move)
        
        return bad

    def new_game_state(self, origin_square, selected_square, piece_id):
        # make a new grid and then generate the new white/black pieces list, and the list of squares
        self.game_states[f'{str(float(self.move_number))}|{self.white_turn}'] = deepcopy(self.GRID)  # i am fucking paranoid
        self.GRID = self.new_move(origin_square.pos, selected_square.pos, piece_id, checking_enpassant=True, checking_castling=True, promotion=True)
        self.black_pieces, self.white_pieces, self.squares = self.create_grid(self.GRID)
# they are fucking after me man 
        # if en passant is possible                     
        if self.enpassant_pawn != None:
            pieces = self.black_pieces if not self.white_turn else self.white_pieces

            for piece in pieces:
                if piece.class_value == 'pawn':
                    if piece.x // self.Xtl == self.enpassant_pawn[0] and piece.y // self.Ytl == self.enpassant_pawn[1]:
                        piece.enpassant = True

        self.is_humans_turn = self.determine_if_humans_turn(self.is_humans_turn)
        self.white_turn = not self.white_turn
        self.move_number += 0.5  # this is very lazy lmfao, just floor divide when i want the actual move number value

        # eventually, i will make an end screen
        outcome = self.checkmate()
        if outcome == 1:
            winner = 'White' if not self.white_turn else 'Black'
            print(f"CHECKMATE! {winner} has won the game in {math.floor(self.move_number)} moves!")
            return True
        
        elif outcome == 2:
            print(f"After {math.floor(self.move_number)} moves, the game has been drawn.")
            return True

        elif outcome == 3:
            print(f"After {math.floor(self.move_number)} moves, there is insufficient material, and the game has been drawn.")
            return True

        elif outcome == 0:
            pass

        if self.move_number >= 150:
            print(f'Game has lasted for 150 moves so will be restarted')
            return True

    def checkmate(self):
        player_list = self.white_pieces if self.white_turn else self.black_pieces
        enemy_list = self.black_pieces if self.white_turn else self.white_pieces
        player_move = []  # not specific moves, but just checks to see that there exist at least one legal move

        # checks for insufficient material
        if len(player_list) <= 2 and len(enemy_list) <= 2:
            if len(player_list) == 1 and len(enemy_list) == 1:  # only kings on the board (or else something has gone very, very wrong)
                return 3

            # ensures that first element is not the king, so that the second piece can be checked
            [king := square for square in player_list if square.class_value == 'king']
            player_list.remove(king)
            player_list.append(king)

            [king := square for square in enemy_list if square.class_value == 'king']
            enemy_list.remove(king)
            enemy_list.append(king)

            other_piece = player_list[0].class_value
            enemy_other_piece = enemy_list[0].class_value

            if other_piece == 'knight' or other_piece == 'bishop':
                if len(enemy_list) == 1:  # only king
                    return 3
                
                if enemy_other_piece == 'knight' or enemy_other_piece == 'bishop':
                    return 3

        for piece in player_list:

            moves = piece.valid_moves(self.squares)

            square = self.squares[piece.y // self.Ytl][piece.x // self.Xtl] 
            if piece.class_value == 'king':
                king = square
            
            #TODO: just use the new method
            # or... idk it works so why change it
            for move in moves:
                
                future_state = self.new_move(square.pos, move.pos, piece.id)
                future_black_pieces, future_white_pieces, future_squares_list = self.create_grid(future_state)

                opposite_pieces_list = future_black_pieces if self.white_turn else future_white_pieces

                if self.white_turn:
                    opposite_pieces_list = future_black_pieces
                    player_pieces_list = future_white_pieces

                else:
                    opposite_pieces_list = future_white_pieces
                    player_pieces_list = future_black_pieces
                
                if self.is_legal_position(future_squares_list, player_pieces_list, opposite_pieces_list):
                    player_move.append(move)

        if player_move == []:
            enemy_moves = []
            for piece in enemy_list:
                [enemy_moves.append(move) for move in piece.valid_moves(self.squares)]

            if king in enemy_moves:  # checkmate
                return 1
            
            # else: stalemate
            return 2
        
        return 0

    def check_castling(self, squares, white_pieces, black_pieces, short=False, longue=False):  # short, false will both

        enemy_moves = []
        player_moves = []

        if self.white_turn:

            # get the respective moves list of both colours
            for piece in black_pieces:
                moves = piece.valid_moves(squares)
                [enemy_moves.append(move) for move in moves if move not in enemy_moves]
            
            for piece in white_pieces:
                moves = piece.valid_moves(squares)
                [player_moves.append(move) for move in moves if move not in player_moves]

            # king or both rooks have moved
            if not self.white_castling_possible:
                return False

            if not self.is_legal_position(squares, white_pieces, black_pieces):
                return False
            
            if short:
                if not self.king_castle_short_white:
                    return False

                if squares[7][5] in enemy_moves or squares[7][6] in enemy_moves:
                    return False
                
                if squares[7][5].piece is not None or squares[7][6].piece is not None:
                    return False
                
            elif longue:
                if not self.king_castle_long_white:
                    return False

                if squares[7][3] in enemy_moves or squares[7][2] in enemy_moves:
                    return False
                
                if squares[7][3].piece is not None or squares[7][2].piece is not None or squares[7][1].piece is not None:
                    return False

        else:
            for piece in white_pieces:
                moves = piece.valid_moves(squares)
                [enemy_moves.append(move) for move in moves if move not in enemy_moves]

            for piece in black_pieces:
                moves = piece.valid_moves(squares)
                [player_moves.append(move) for move in moves if move not in player_moves]
            
            if not self.black_castling_possible:
                return False

            if not self.is_legal_position(squares, black_pieces, white_pieces):
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

    def check_colour_turn(self, piece):
        """
        i dont remember why i made this function and what bug it "fixes"
        """

        if self.white_turn:
            if piece.colour == 'w':
                return True
            
        elif not self.white_turn:
            if piece.colour == 'b':
                return True
            
        return False

    def determine_if_humans_turn(self, humans_turn):

        if self.white_AI and self.black_AI:
            return False

        if self.white_turn:
            if humans_turn:
                if self.black_AI:
                    return False
            
            else:
                if self.white_AI:
                    return True
            
        else:
            if humans_turn:
                if self.white_AI:
                    return False
            
            else:
                if self.black_AI:
                    return True

        return True

    def is_legal_position(self, squares, player_pieces_list, enemy_pieces_list):  # squares for new game state, player_pieces_list to check moves against the players king, enemy_pieces_list for all legal moves of the opposite player
        
        """
        make a state of the future board using the new grid given.
        if the players king is exposed by new state legal moves, return False
        if the players king is not, then it is a legal move, return True
        call this function in a loop of all the legal moves that can be made by the piece
        """
        
        king = None

        # find the player's king
        for piece in player_pieces_list:
            if piece.class_value == 'king':
                square_x, square_y = piece.x // self.Xtl, piece.y // self.Ytl
                king = squares[square_y][square_x]

        # [print(i) for i in squares]
        # print(player_pieces_list)
        # print(enemy_pieces_list)

        if king is None:  # Inshaallah this works
            return False
        # assert king is not None  # this might fix some bullshit  # this doesnt fix any bullshit  # it now exists as a relic of my stupidity
        
        enemy_moves = []
        for piece in enemy_pieces_list:
            moves = piece.valid_moves(squares)
            [enemy_moves.append(move) for move in moves]
                
        # check if king is in the enemies move list
        if king in enemy_moves:
            return False
        
        return True

    def update(self):
        self.display.fill(self.cl['b'])

        for row in self.squares:
            for square in row:

                if square.clicked:
                    square.colour = self.cl['bg'] # change colour to other than dg

                elif square.legal_move:
                    square.colour = self.cl['dg']

                else:
                    square.colour = square.normal_colour

                square.draw()

                if square.piece != None:
                    square.piece.draw()

        pygame.display.update()

    def start(self):
        self.black_pieces, self.white_pieces, self.squares = self.create_grid(self.GRID)

        if self.white_AI:
            self.white_bot = ChessEngine(self, 'w')
        
        if self.black_AI:
            self.black_bot = ChessEngine(self, 'b')

        self.run = True

        while self.run:

            self.clock.tick(self.FPS)
            if self.events():
                return True
        
            self.update()

            if self.white_AI and self.white_turn:
                origin_square, move, piece_id = self.white_bot.generate_move(self.squares, self.white_pieces, self.black_pieces)
                if self.new_game_state(origin_square, move, piece_id):
                    return True

            elif self.black_AI and not self.white_turn:
                origin_square, move, piece_id = self.black_bot.generate_move(self.squares, self.white_pieces, self.black_pieces)
                if self.new_game_state(origin_square, move, piece_id):
                    return True
# i hear voices in the walls......

def main():

    game = Game()
    if game.start():
        main()  # lol

if __name__ == '__main__':
    main()
