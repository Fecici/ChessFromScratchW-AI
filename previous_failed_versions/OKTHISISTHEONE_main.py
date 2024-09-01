"""
Ideas:
- import random and make an ai that randomly chooses moves, then actually train an ai against that ai
or sum shit like that

"""

import pygame; import math; import random; import sys; from copy import deepcopy; from Chess.previous_failed_versions.OKTHISISTHEONE_pieces import King, Queen, Pawn, Bishop, Knight, Rook

outside_class_grid = [ # first letter is colour, second is piece in chess notation, 00 is empty
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr'],
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
        # if self.clicked:
        #     self.colour = self.game.cl['bg'] # change colour to other than dg
        #
        # elif self.legal_move:
        #     self.colour = self.game.cl['dg']
        #
        # else:
        #     self.colour = self.normal_colour
        
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
        self.FPS = 60

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
        self.game_states = {}  # could write to json file? each state could have its info stored in json for ease of access

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
        """

        """
        this may be some bullshit:

        i am going to encode a list. I will
        iterate through the self.GRID list and
        add an extra fucking zero at the end
        of each string. then, i will manipulate it
        an then finally, remove the zero. then, that list will be returned
        - all this because python fucks with lists with different references or smth like that


        o my god why does it work
        its so fucking retarded
        looking at it gives me an
        anueriusm
        anneurismn
        how the gfuck do you spell anneurism
        aneurysm
        looking at it gives me an aneurysm
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
                            

                        # if short
                        elif x1 == 7 and y1 == 7:
                            self.king_castle_short_white = False
                            
            
            elif piece == 'br':
                for item in self.black_pieces:

                    if item.x // self.Xtl == x1 and item.y // self.Ytl == y1 and item.class_value == 'rook':  # see above

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
                new_new_row.append(new_sq[:2])  # this is unbelievably fucking dumb and genius at the same time  # its not genius, its just dumb
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
                    [print(i) for i in self.white_pieces]
                
                if key_list[pygame.K_LSHIFT] and key_list[pygame.K_b]:
                    print('\nBLACK PIECES:')
                    [print(i) for i in self.black_pieces]
                
                # if key_list[pygame.K_c]:
                #     self.debug_checkmate = not self.debug_checkmate

                if key_list[pygame.K_r]:
                    return True

            if event.type == pygame.MOUSEBUTTONDOWN: # test MOUSEBUTTONUP vs MOUSEBUTTONDOWN, main goal is to avoid unintentional spammed button clicks on squares

                pos = pygame.mouse.get_pos()  # why is pos unused but used at the same time?

                for row in self.squares:
                    for square in row:
                        if square.rect.collidepoint(pos):
                            selected_square = square
                            # the logic may be broken here

                            # it's very broken here

                            # yay no more broken

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
                                
                                    if self.check_colour_turn(self.selected_square.piece):
                                        # this check should stop bugs in the enemy move check thing
                                        self.squares_to_move = self.selected_square.piece.valid_moves(self.squares)

                                        # print(len(self.squares_to_move))
                                        bad = []
                                        # removes all illegal moves from the move list
                                        if self.selected_square.piece.class_value == 'king':

                                            if self.white_turn:
                                                if self.check_castling(short=True):  self.squares_to_move.append(self.squares[7][6])
                                                if self.check_castling(longue=True): self.squares_to_move.append(self.squares[7][2])

                                            else:
                                                if self.check_castling(short=True):  self.squares_to_move.append(self.squares[0][6])
                                                if self.check_castling(longue=True): self.squares_to_move.append(self.squares[0][2])

                                            # if self.move_number <= 0.5:
                                            #     if self.selected_square.piece.colour == 'w':
                                            #         self.squares_to_move.remove(self.squares[7][6])
                                            #         self.squares_to_move.remove(self.squares[7][2])

                                            #     elif self.selected_square.piece.colour == 'b':
                                            #         self.squares_to_move.remove(self.squares[0][6])
                                            #         self.squares_to_move.remove(self.squares[0][2])
                                                    
                                            #TODO: check if the king is actually able to castle any side over here first to avoid removing the wrong squares for no reason
                                            """
                                            check all of the conditions needed for castling to occur.
                                            if this check fails, the move is removed from self.squares_to_move
                                            """
                                            
                                            # for check
                                            """

                                            TODO: different approach: make a check to see if castling is legal
                                            similar to how other legal moves were checked. but then how to figure out
                                            other moves when looping through enemy moves? make a check perhaps? there
                                            is no possible situation where the king could castle into check anyways, so
                                            perhaps if there is a flag in the valid_moves() method, this may work well.
                                            this also means that all flags can be checked at the same time

                                            then, legal castling is always true in the king class
                                            until it is not.

                                            NEW NEW METHOD

                                            castling true at the start of the game --> 4 variables for each colour, short/long castling
                                            then each king that gets initialized should have castling immediately checked for true/false
                                            and the rooks should have the same thing each, checking 4 cases for 4 rooks, same thing once again.
                                            --> involves checking the starting square and then checking the appropriate bool - done

                                            then in game, when the king is clicked, if it is able to castle long or short, check that appropriate side
                                            --> start with checking for check, then check if the 2 adjacent squares are controlled by the enemy pieces
                                            the logic should then be much easier to write 

                                            the logic should now be correct below


                                            TODO: nope its still fucked
                                            ok what the fuck is happening here
                                            problem with white king is diff



                                            wait... what if the king goes False first, 
                                            and then if castling is allowed, we add it 
                                            here? instead of getting it returned in the 
                                            valid_moves() method? - there are still problems with this

                                            ok, how the fuck is it still broken??? what have i done??? like, 
                                            short castling is never allowed, andlong castling is always allowed? 
                                            whay, why is this so fujke d yp ujp up??;
                                            """
# oh man i farted and it STINKS
                                            # current_pieces = (self.white_pieces, self.black_pieces) if self.white_turn else (self.black_pieces, self.white_pieces)  # this is bad practice i think, but [0] is the current player and [1] is the enemy
                                            # checks for checks
                                            # enemy_moves = []
                                            # for piece in current_pieces[1]:
                                            #     moves = piece.valid_moves(self.squares)
                                            #     [enemy_moves.append(move) for move in moves]  # this is used later to ensure the king is not in check

                                            # this should immediately skip unnecessary steps  # acc naahhhh im too lazy for optimization
                                            # for white king
                                            """
                                            I AM SO RETARTED BRO...

                                            if i am removing the square from the move list, then even if i dont intend to castle,
                                            the king will never be able to move there

                                            i basically need to check that the king is actually sitting on the starting square before i remove anything

                                            ^^^^this is fixed now


                                            the variables need to be rewritten, somewhat. the game attributes for king and rook castling
                                            should be reflective of whether castling is even still possible.
                                            what needs to be checked:
                                            - if castling has already occurred, set the respective possibility variables to false.
                                            - if the king is in check, castling in that instance is not possible.
                                            - if the 2 adjacent squares are under fire, castling is not possible.
                                            - if the 2 adjacent squares have pieces on them, castling is not possible.
                                            - if the rook or king has moved, castling is not possible on that side or either side respectively.

                                            maybe a function should be made that simply returns a bool if these conditions are met?
                                            that seems like the best course of action
                                            
                                            it works...
                                            holy shit nvm
                                            it FUCKN WORKS NOW LESGOOOO
                                            it doesnt work lol

                                            #TODO: do this and redo all castling

                                            new tech: just make a function that checks all the cases everytime a move is run 
                                            (takes self.white_turn as a parameter), and check game attr variables to ensure that the king/rook havent moved
                                            from their respective spots and/or if castling hasnt already occured. this will follow this following flow:
                                            - check that castling is even possible anymore for the respective side
                                            - check that the spaces are unoccupied
                                            - check that the king is not in check
                                            - check that neither space is under attack from enemy pieces
                                            - finally, return true

                                            the game attr variables will store which rook has moved, and if the king has moved
                                            (that side is unavailable for that colour, that side cannot castle, respectively)
                                            --> the pieces themselves will not need to store any attributes related to castling.
                                            --> the new_move() method may need to (will need to) be reworked for castling

                                            who wouldve guessed that actually following proper programming procedures would make this problem simple and easy?
                                            """
                                            # if self.selected_square.piece.colour == 'w' and self.king_castle_long_white and self.king_castle_short_white:
                                                
                                            #     # check if we can just remove moves here if the rook or king cannot move w/out computing all this shit later
                                            #     if not self.king_castle_short_white or not self.rook_castle_short_white:

                                            #         if self.squares[7][6] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[7][6])

                                            #     if not self.king_castle_long_white or not self.rook_castle_long_white:
                                                    
                                            #         if self.squares[7][2] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[7][2])

                                            #     # disallows castling if in check
                                            #     if not self.check_legal_moves(self.squares, current_pieces[0], current_pieces[1]):

                                            #         if self.squares[7][6] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[7][6])

                                            #         if self.squares[7][2] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[7][2])
                                                
                                            #     # checks that the squares are not under enemy control or are being blocked
                                            #     # changes only the piece attribute
                                            #     # this checks for interfering attacks (fucking bishops)
                                            #     #TODO: check to see if the moves are axtually the same type as the other thing
                                            #     else:
                                            #         if self.selected_square.piece.castling_short:
                                            #             if (self.squares[7][5] in enemy_moves or self.squares[7][6] in enemy_moves) or (self.squares[7][5].piece != None or self.squares[7][6].piece != None):

                                            #                 if self.squares[7][6] in self.squares_to_move:
                                            #                     self.squares_to_move.remove(self.squares[7][6])

                                            #         if self.selected_square.piece.castling_long:
                                            #             if (self.squares[7][2] in enemy_moves or self.squares[7][3] in enemy_moves) or (self.squares[7][2].piece != None or self.squares[7][3].piece != None):

                                            #                 if self.squares[7][2] in self.squares_to_move:
                                            #                     self.squares_to_move.remove(self.squares[7][2])

                                            # # for black king
                                            # elif self.selected_square.piece.colour == 'b' and self.king_castle_long_black and self.king_castle_short_black:
                                                
                                            #     if not self.king_castle_short_black or not self.rook_castle_short_black:
                                            #         if self.squares[0][6] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[0][6])

                                            #     if not self.king_castle_long_black or not self.rook_castle_long_black:

                                            #         if self.squares[0][2] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[0][2])

                                            #     if not self.check_legal_moves(self.squares, current_pieces[0], current_pieces[1]):
                                                    
                                            #         if self.squares[0][6] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[0][6])

                                            #         if self.squares[0][2] in self.squares_to_move:
                                            #             self.squares_to_move.remove(self.squares[0][2])

                                            #     else:

                                            #         if self.selected_square.piece.castling_short:  # inshaallah this thing is the right bool

                                            #             if (self.squares[0][5] in enemy_moves or self.squares[0][6] in enemy_moves) or (self.squares[0][5].piece != None or self.squares[0][6].piece != None):

                                            #                 if self.squares[0][6] in self.squares_to_move:
                                            #                     self.squares_to_move.remove(self.squares[0][6])

                                            #         if self.selected_square.piece.castling_long:

                                            #             if (self.squares[0][2] in enemy_moves or self.squares[0][3] in enemy_moves) or (self.squares[0][2].piece != None or self.squares[0][3].piece != None):

                                            #                 if self.squares[0][2] in self.squares_to_move:
                                            #                     self.squares_to_move.remove(self.squares[0][2])

                                        for move in self.squares_to_move:  # 'move' is a Square object

                                            """
                                            this took years from my lifespan for no fukckn reason
                                            """
                                            future_state = []
                                            
                                            """
                                            this new_move() thing must be whee the values are getting changed for no reason
                                            """
                                            # print(f"""
                                            #         white rook long castle:  {self.rook_castle_long_white}
                                            #         white rook short castle: {self.rook_castle_short_white}
                                            #         white king long castle:  {self.king_castle_long_white}
                                            #         white king short castle: {self.king_castle_short_white}
                                                                
                                            #         black rook long castle:  {self.rook_castle_long_black}
                                            #         black rook short castle: {self.rook_castle_short_black}
                                            #         black king long castle:  {self.king_castle_long_black}
                                            #         black king short castle: {self.king_castle_short_black}
                                            #     """)

                                            future_state = self.new_move(self.selected_square.pos, move.pos, self.selected_square.piece.id)
                                            
                                            # print(f"""
                                            #         white rook long castle:  {self.rook_castle_long_white}
                                            #         white rook short castle: {self.rook_castle_short_white}
                                            #         white king long castle:  {self.king_castle_long_white}
                                            #         white king short castle: {self.king_castle_short_white}
                                                                
                                            #         black rook long castle:  {self.rook_castle_long_black}
                                            #         black rook short castle: {self.rook_castle_short_black}
                                            #         black king long castle:  {self.king_castle_long_black}
                                            #         black king short castle: {self.king_castle_short_black}
                                            #     """)
                                            future_black_pieces, future_white_pieces, future_squares_list = self.create_grid(future_state)

                                            # [print(i) for i in future_state]
                                            # print('\n\n')
                                            # [print(o) for o in future_squares_list]

                                            opposite_pieces_list = future_black_pieces if self.white_turn else future_white_pieces
                                            if self.white_turn:
                                                opposite_pieces_list = future_black_pieces
                                                player_pieces_list = future_white_pieces
                                            else:
                                                opposite_pieces_list = future_white_pieces
                                                player_pieces_list = future_black_pieces
                                            
                                            if not self.check_legal_moves(future_squares_list, player_pieces_list, opposite_pieces_list):  # why is my king gone after like move 5
                                                # print(f'REMOVED: {move}')
                                                bad.append(move)

                                        #TODO: if bad == self.squares_to_move: check if other king is fucked. if so, checkmate. else, stalemate.
                                        [self.squares_to_move.remove(move) for move in bad]
                                        for s in self.squares_to_move:  # highlight the legal moves
                                            s.legal_move = True
                            
                            # if the selected square isn't itself and it is a legal move (a move has been played)
                            elif selected_square != self.selected_square and selected_square.legal_move:
                                self.game_states[f'{str(float(self.move_number))}|{self.white_turn}'] = deepcopy(self.GRID)  # i am fucking paranoid
                                self.GRID = self.new_move(self.selected_square.pos, selected_square.pos, self.selected_square.piece.id, checking_enpassant=True, checking_castling=True, promotion=True)
                                self.black_pieces, self.white_pieces, self.squares = self.create_grid(self.GRID)
# they are fucking after me man                      
                                if self.enpassant_pawn != None:
                                    pawns = self.black_pieces if not self.white_turn else self.white_pieces
                                    for pawn in pawns:  # technically, pawns is a list of all the pieces but... shut up
                                        if pawn.class_value == 'pawn':  # this is very funny
                                            if pawn.x // self.Xtl == self.enpassant_pawn[0] and pawn.y // self.Ytl == self.enpassant_pawn[1]:
                                                pawn.enpassant = True

                                self.white_turn = not self.white_turn
                                self.move_number += 0.5  # this is very lazy lmfao, just floor divide when i want the actual move number value

                                # if self.debug_checkmate:
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
                                    print('nothing')
                                    
                                # [print(i) for i in self.game_states[f'{str(self.move_number - 0.5)}|{not self.white_turn}']]
                                # print('\n\n')

                            # if i click on the same square
                            elif selected_square == self.selected_square:
                                selected_square.clicked = False

                                for lines_persisting in self.squares_to_move: # if i forget why this iter name is funny, just ask jodran
                                    lines_persisting.clicked = False
                                    lines_persisting.legal_move = False
                                self.squares_to_move = []
                                self.selected_square = None

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
                if len(enemy_list) == 1:
                    return 3
                
                if enemy_other_piece == 'knight' or enemy_other_piece == 'bishop':
                    return 3

        for piece in player_list:

            moves = piece.valid_moves(self.squares)

            square = self.squares[piece.y // self.Ytl][piece.x // self.Xtl] 
            if piece.class_value == 'king':
                king = square
            
            for move in moves:
                future_state = []
                future_state = self.new_move(square.pos, move.pos, piece.id)

                future_black_pieces, future_white_pieces, future_squares_list = self.create_grid(future_state)

                opposite_pieces_list = future_black_pieces if self.white_turn else future_white_pieces

                if self.white_turn:
                    opposite_pieces_list = future_black_pieces
                    player_pieces_list = future_white_pieces

                else:
                    opposite_pieces_list = future_white_pieces
                    player_pieces_list = future_black_pieces
                
                if self.check_legal_moves(future_squares_list, player_pieces_list, opposite_pieces_list):  # why is my king gone after like move 5
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

    def check_castling(self, short=False, longue=False):  # short, false will both

        enemy_moves = []
        player_moves = []

        if self.white_turn:

            # get the respective moves list of both colours
            for piece in self.black_pieces:
                moves = piece.valid_moves(self.squares)
                [enemy_moves.append(move) for move in moves if move not in enemy_moves]
            
            for piece in self.white_pieces:
                moves = piece.valid_moves(self.squares)
                [player_moves.append(move) for move in moves if move not in player_moves]

            # king or both rooks have moved
            if not self.white_castling_possible:
                return False

            if not self.check_legal_moves(self.squares, self.white_pieces, self.black_pieces):
                return False
            
            if short:
                if self.squares[7][5] in enemy_moves or self.squares[7][6] in enemy_moves:
                    return False
                
                if self.squares[7][5].piece is not None or self.squares[7][6].piece is not None:
                    return False
                
            elif longue:
                if self.squares[7][3] in enemy_moves or self.squares[7][2] in enemy_moves:
                    return False
                
                if self.squares[7][3].piece is not None or self.squares[7][2].piece is not None or self.squares[7][1].piece is not None:
                    return False

        else:
            for piece in self.white_pieces:
                moves = piece.valid_moves(self.squares)
                [enemy_moves.append(move) for move in moves if move not in enemy_moves]

            for piece in self.black_pieces:
                moves = piece.valid_moves(self.squares)
                [player_moves.append(move) for move in moves if move not in player_moves]
            
            if not self.black_castling_possible:
                return False

            if not self.check_legal_moves(self.squares, self.black_pieces, self.white_pieces):
                return False
            
            if short:
                if self.squares[0][5] in enemy_moves or self.squares[0][6] in enemy_moves:
                    return False
                
                if self.squares[0][5].piece is not None or self.squares[0][6].piece is not None:
                    return False
                
            elif longue:
                if self.squares[0][3] in enemy_moves or self.squares[0][2] in enemy_moves:
                    return False
                
                if self.squares[0][3].piece is not None or self.squares[0][2].piece is not None or self.squares[0][1].piece is not None:
                    return False

        return True

    def check_colour_turn(self, piece):

        if self.white_turn:
            if piece.colour == 'w':
                return True
            
        elif not self.white_turn:
            if piece.colour == 'b':
                return True
            
        return False

    def check_legal_moves(self, squares, player_pieces_list, enemy_pieces_list):  # squares for new game state, player_pieces_list to check moves against the players king, enemy_pieces_list for all legal moves of the opposite player
        
        """
        make a state of the future board using the new grid given.
        if the players king is exposed by new state legal moves, return False
        if the players king is not, then it is a legal move, return True
        call this function in a loop of all the legal moves that can be made by the piece

        need to get the king to work normally with types
        need to get the king's square pos, not the piece itself
        """
        
        king = None
        # print('\n\n')
        # [print(player) for player in player_pieces_list]
        # print('\n\n')

        # find the player's king
        for piece in player_pieces_list:
            if piece.class_value == 'king':
                square_x, square_y = piece.x // self.Xtl, piece.y // self.Ytl
                king = squares[square_y][square_x]

        if king is None:  # this might fix some bullshit  # this doesnt fix any bullshit
            raise ValueError  # this means we are fucked
        # print(king)
        
        enemy_moves = []
        for piece in enemy_pieces_list:
            moves = piece.valid_moves(squares)
            [enemy_moves.append(move) for move in moves]
                
        # check if king is in the enemies move list
        if king in enemy_moves:
            return False
        
        # print('returning true')
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
        self.black_pieces, self.white_pieces, self.squares = self.create_grid(self.GRID) #

        self.run = True

        while self.run:

#             print(f"""
#     white rook long castle:  {self.rook_castle_long_white}
#     white rook short castle: {self.rook_castle_short_white}
#     white king long castle:  {self.king_castle_long_white}
#     white king short castle: {self.king_castle_short_white}
                  
#     black rook long castle:  {self.rook_castle_long_black}
#     black rook short castle: {self.rook_castle_short_black}
#     black king long castle:  {self.king_castle_long_black}
#     black king short castle: {self.king_castle_short_black}
# """)
            self.clock.tick(self.FPS)
            if self.events():
                return True
            self.update()
# i hear voices in the walls......

def main():
    game = Game()
    if game.start():
        main()  # lol

if __name__ == '__main__':
    main()
