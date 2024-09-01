"""
redo the valid_moves() method so that a position is used instead of the Game class.
move all relevant methods to that class, such as checking for castling, illegal moves,
is legal position, etc. the game can store castling booleans here for use in the positions
class, but new_move method should also be moved so that it can simulate positions when 
using the minimax alpha beta search

ideas:
- check if AI is playing a position before doing all of the valid move calculations on it
- bitboards, bitboards, bitboards
- magic bitboards for sliding pieces
- find all potential moves and then remove the illegal moves from them when initializing the position class
- use more functions to make the code more readable
- literally just need to optimize making new moves
- prevent all graphical calculations when doing position search. this may include the rects in the squares/pieces classes
- find a way to combine the legal move generation and children attributes of the positions class to optimize it
- maybe all human interactions like promotion interface should be kept in main.py?
- stop creating new squares every time the position is made. simply change the piece attribute?
--> or, keep making new squares but dont render the rect stuff or anything to do with ui when searching positions
- when pieces are made, same thing. dont calculate the ui stuff for positions search
- store king position in position attributes
- we dont actually need to generate the moves list for terminal moves, do we? this could save a lot of computation time

Current bugs:
- promotions dont work (probably b/c i literally copy and pasted the new move code into the positions thing) --> the code isnt actually detecting possible promotions or enpassant when a human is playing it
- enpassant doesnt work but for black it has a delayed reaction???? i commented that bit of code for now
- not enough positions are searched at depth 5. this is probably due to enpassant, promotion, and/or castling. 110k positions are missed
- not a bug, but taking 60 seconds to search 9300 positions is insanely bad
- the low speed is because of the unoptimized move generation. many things should be done to fix this.
"""

import pygame; import math; import random; import time; import sys; from copy import deepcopy; from chessEngine import *

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

        # x val of get_sprite() is multiplied by the image's place in the sequence on the spritesheet, starting from 0
        self.graphics = {
            'wk': self.spritesheet.get_sprite(120 *  7, 0, self.Xtl, self.Ytl),
            'wq': self.spritesheet.get_sprite(120 * 10, 0, self.Xtl, self.Ytl),
            'wp': self.spritesheet.get_sprite(120 *  9, 0, self.Xtl, self.Ytl),
            'wr': self.spritesheet.get_sprite(120 * 11, 0, self.Xtl, self.Ytl),
            'wb': self.spritesheet.get_sprite(120 *  6, 0, self.Xtl, self.Ytl),
            'wn': self.spritesheet.get_sprite(120 *  8, 0, self.Xtl, self.Ytl),
            'bk': self.spritesheet.get_sprite(120 *  1, 0, self.Xtl, self.Ytl),
            'bq': self.spritesheet.get_sprite(120 *  4, 0, self.Xtl, self.Ytl),
            'bp': self.spritesheet.get_sprite(120 *  3, 0, self.Xtl, self.Ytl),
            'br': self.spritesheet.get_sprite(120 *  5, 0, self.Xtl, self.Ytl),
            'bb': self.spritesheet.get_sprite(120 *  0, 0, self.Xtl, self.Ytl),
            'bn': self.spritesheet.get_sprite(120 *  2, 0, self.Xtl, self.Ytl)
        }

        self.grid = outside_class_grid

        self.testing_grid = [  # TESTING ONLY
            ['br', 'bn', 'bb', 'bq', '00', 'bk', '00', 'br'],
            ['bp', 'bp', '00', 'wp', 'bb', 'bp', 'bp', 'bp'],
            ['00', '00', 'bp', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', 'wb', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['wp', 'wp', 'wp', '00', 'wn', 'bn', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', '00', '00', 'wr']
        ]

        self.GRID = self.testing_grid
        self.position = None

        self.white_king = None
        self.black_king = None

        #TODO: squares, moves, enpassant_pawn, castling will stay but behaviour will change
        self.squares = []  # contains all of the squares in the board

        self.white_pieces = []
        self.black_pieces = []

        # store the possible moves after each gamestate for faster checks
        # only has information on controlled squares
        self.white_moves = []
        self.black_moves = []

        self.white_moves_unculled = []
        self.black_moves_unculled = []

        self.squares_to_move = []  # these are all legal moves that the selected piece can move
        self.selected_square = None  # the selected square
        self.enpassant_pawn = None

        # debug
        self.debug_checkmate = False
        self.debug_castling = False
        self.debug_move_search = True
        self.manual_move_debug = not True
        self.debug_position_making = False
        self.debug_illegal_moves = False

        self.positions_searched = 0 
        self.different_positions_grid = {}

        # different cases for the board
        self.king_castle_long_white = self.king_castle_long_black = self.king_castle_short_black = self.king_castle_short_white = True  # this will be reused - checks if either side is possible, is different from the other variable as it checks if the rooks have moved, not the king
        self.white_castling_possible = self.black_castling_possible = True

        self.white_turn = True
        self.move_number = 0
        self.game_states = {}  # could write to json file? each state could have its info stored in json for ease of access. this could just be a regular dict that stores all the relevant gamestate attributes

        # AI stuff
        self.white_AI = not True
        self.black_AI = not True


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
    
    def promotion(self, x, white=False, black=False):  # x is just the x coordinate

        """
        TODO: must rework how the promotion gets calculated

        nahh its good, it works in the position class
        """
        
        promotion_run = True
        promoted_piece = False  # if this remains false until after the while loop, something has gone very wrong

        # this could have just gone to the __init__() method but who fuckin cares lol
        white_sprites = [
            (self.graphics['wq'], 'wq'), 
            (self.graphics['wr'], 'wr'), 
            (self.graphics['wn'], 'wn'), 
            (self.graphics['wb'], 'wb')
            ]
        
        black_sprites = [
            (self.graphics['bq'], 'bq'), 
            (self.graphics['br'], 'br'), 
            (self.graphics['bn'], 'bn'), 
            (self.graphics['bb'], 'bb')
            ]
        
        promotion_squares = []

        if white: sprites = white_sprites
        elif black: sprites = black_sprites[::-1]  # reverse because it looks nicer

        c = 0 if white else 4  # just a magic number to help fix the y pos for black. just shifts it down 4 squares

        for i in range(4):
            promotion_square = Square(self, x, i + c, 'w', pygame)
            promotion_square.graphic = sprites[i][0],
            promotion_square.graphic_id = sprites[i][1]
            promotion_squares.append(promotion_square)

        #TODO: this is so stupid, remove this and dont use random. just include this as a child in the positions class
        while promotion_run:
            # if self.white_turn and self.white_AI:
            #     promoted_piece = random.choice(promotion_squares).graphic[1]
            #     promotion_run = False
            #     break

            # elif not self.white_turn and self.black_AI:
            #     promoted_piece = random.choice(promotion_squares).graphic[1]
            #     promotion_run = False
            #     break
            
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    for square in promotion_squares:
                        if square.rect.collidepoint(pos):
                            promoted_piece = square.graphic_id
                            promotion_run = False

            for square in promotion_squares:
                square.draw(default=False)
            pygame.display.update()

        return promoted_piece

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
                
                if key_list[pygame.K_c]:
                    print(f'DEBUG CHECKMATE: {not self.debug_checkmate}')
                    self.debug_checkmate = not self.debug_checkmate

                if key_list[pygame.K_x]:
                    self.debug_castling = not self.debug_castling
                    print(self.debug_castling)

                if key_list[pygame.K_p]:
                    self.debug_position_making = not self.debug_position_making
                    print(self.debug_position_making)

                if key_list[pygame.K_i]:
                    self.debug_illegal_moves = not self.debug_illegal_moves
                    print(self.debug_illegal_moves)

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
                                if self.debug_castling:
                                    pass  # breakpoint goes here

                                moves, bad_moves = self.selected_square.piece.valid_moves(self.squares, cull_illegal_moves=True, add_castling=True)
                                for move in bad_moves:
                                    moves.remove(move)

                                self.squares_to_move = moves

                            else:
                                if self.debug_illegal_moves:
                                    pass
                                moves, bad_moves = self.selected_square.piece.valid_moves(self.squares, cull_illegal_moves=True)
                                # print(moves, bad_moves)
                                for move in bad_moves:
                                    moves.remove(move)
                                # print(moves, bad_moves)
                                
                                self.squares_to_move = moves

                            for s in self.squares_to_move:  # highlight the legal moves
                                s.legal_move = True
                
                # if the selected square isn't itself and it is a legal move (a move has been played)
                elif selected_square != self.selected_square and selected_square.legal_move:

                    # updates the game state; the conditional only applies for checkmate/stalemate
                    if self.new_game_state(self.GRID, self.selected_square, selected_square, self.selected_square.piece.id):
                        return True

                # if i click on the same square
                elif selected_square == self.selected_square:
                    selected_square.clicked = False

                    for lines_persisting in self.squares_to_move: # if i forget why this iter name is funny, just ask jodran
                        lines_persisting.clicked = False
                        lines_persisting.legal_move = False
                    self.squares_to_move = []
                    self.selected_square = None

    def new_game_state(self, grid, origin_square, selected_square, piece_id):  # This must stay inside of the main file
        # make a new grid and then generate the new white/black pieces list, and the list of squares
        if self.debug_position_making:
            # print('debugging')
            pass
        # this can be redone with the positions class now
        self.game_states[f'{str(float(self.move_number))}|{self.white_turn}'] = deepcopy(grid)  # i am fucking paranoid

        if piece_id == 'wk':
            self.white_king = selected_square
        elif piece_id == 'bk':
            self.black_king = selected_square
        
        self.GRID = self.position.new_move(grid, origin_square.pos, selected_square.pos, piece_id, checking_enpassant=True, checking_castling=True, promotion=True)
        
        self.king_castle_long_black = self.position.king_castle_long_black
        self.king_castle_long_white = self.position.king_castle_long_white
        self.king_castle_short_black = self.position.king_castle_short_black
        self.king_castle_short_white = self.position.king_castle_short_white

        self.white_castling_possible = self.white_castling_possible
        self.black_castling_possible = self.black_castling_possible

        if self.debug_castling:
            pass
        
        # print(f'\nGAMESTATE METHOD: ENPASSANT PAWN BEFORE ASSIGNMENT: {self.enpassant_pawn}')
        self.enpassant_pawn = self.position.enpassant_pawn  # if there was an enpassant, it will be known after the new_moves method
        # print(f'GAMESTATE METHOD: ENPASSANT PAWN AFTER ASSIGNMENT: {self.enpassant_pawn}\n')

        self.is_humans_turn = self.determine_if_humans_turn(self.is_humans_turn)
        self.white_turn = not self.white_turn

        # print(f'\nIN MAIN.PY: {self.enpassant_pawn}\n')

        print('Time needed for position instance')
        t = time.time()

        self.position = Position(self, 
                                 (origin_square, selected_square), 
                                 self.white_turn,
                                 self.GRID, 
                                 pygame, 
                                 self.king_castle_long_white,
                                 self.king_castle_long_black,
                                 self.king_castle_short_black,
                                 self.king_castle_short_white,
                                 self.white_castling_possible,
                                 self.black_castling_possible,
                                 self.enpassant_pawn,
                                 self.white_king,
                                 self.black_king
                                 )
        print(f'{time.time() - t} seconds')
        self.black_pieces = self.position.black_pieces
        self.white_pieces = self.position.white_pieces
        # print('NEW PIECES SET IN GAMESTATES METHOD:\n\n')
        # print('WHITE PIECES:\n')
        # [print(i) for i in self.white_pieces]
        # print('BLACK PIECES:\n')

        # [print(i) for i in self.black_pieces]
        self.squares = self.position.board

        self.move_number += 0.5  # floor divide when i want the actual move number value
        self.position.move_number = self.move_number
        # print(f'~~~~~~~~~~~~~[MOVE NUMBER: {self.move_number}]~~~~~~~~~~~~~\n')
        # [print(i) for i in self.GRID]
        # print('\n')

        # eventually, i will make an end screen
        
        outcome = self.position.checkmate()
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

        if self.move_number >= 150:
            print(f'Game has lasted for 150 moves and will be restarted')
            return True

    def check_colour_turn(self, piece):
        """
        i dont remember why i made this function and what bug it "fixes"

        ohhh, i think its just to stop the wrong pieces from generating moves,
        ie if whites turn, black pieces cant be selected
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

        if self.white_AI:
            self.white_bot = ChessEngine(self, 'w')
        
        if self.black_AI:
            self.black_bot = ChessEngine(self, 'b')

        self.run = True

        self.position = Position_V2(
                                 (None, None), 
                                 self.white_turn, 
                                 self.GRID, 
                                 self.king_castle_long_white, 
                                 self.king_castle_long_black, 
                                 self.king_castle_short_black, 
                                 self.king_castle_short_white, 
                                 self.white_castling_possible, 
                                 self.black_castling_possible,
                                 None,
                                 self.white_king,
                                 self.black_king
                                 )
        
        # self.white_moves = self.position.white_moves
        # self.black_moves = self.position.black_moves

        for i, row in enumerate(self.GRID):
            for j, val in enumerate(row):
                if val == 'wk':
                    self.white_king = (i, j)

                if val == 'bk':
                    self.black_king = (i, j)

        while self.run:

            # self.clock.tick(self.FPS)
            if self.events():
                return True

            if not self.debug_move_search:
                self.update()

            if self.manual_move_debug:
                moves = [
                    (self.squares[6][4], self.squares[4][4]),  # e4
                    (self.squares[1][3], self.squares[3][3]),  # d5

                    (self.squares[4][4], self.squares[3][4]),  # e5
                    (self.squares[1][5], self.squares[3][5]),  # g5

                    (self.squares[6][4], self.squares[4][4]),  # 
                    (self.squares[6][4], self.squares[4][4]),  # 
                         ]
                
                for new_move in moves:
                    origin_square = new_move[0]
                    move = new_move[1]
                    piece_id = new_move[0].piece.id

                    if self.new_game_state(self.GRID, origin_square, move, piece_id):
                        return True

            if self.debug_move_search:

                """
                idea: use the good but slow move search to find all the needed moves
                and then check which moves are missing after the optimized but bad search
                """

                # import cProfile
                test_engine = ChessEngine(self, 'N/A')
                initial_time = time.time()

                depth = 1
                test_engine.minimax(self.position, True, -1e50, 1e50, depth)
                elapsed_time = time.time() - initial_time
                
                print(f'Searched {self.positions_searched} positions in {elapsed_time} seconds, at depth = {depth}')
                # cProfile.run('test_engine.minimax(self.position, True, float("-inf"), float("inf"), 3)')


                with open('minimax_debug.txt', 'a') as f:
                    for i in self.different_positions_grid:
                        pos = f'\nPOSITION {i}:\n\n'
                        [pos := pos + f'{k}\n' for k in self.different_positions_grid[i]]

                        f.write(pos)

                break

            if self.white_AI and self.white_turn:
                print('\nWHITE IS CHOOSING A MOVE\n')
                # origin_square, move, piece_id = self.white_bot.generate_move(self.squares, self.GRID, self.white_pieces, self.black_pieces)
                rand_pos_debug = random.choice(list(self.position.children.values()))
                origin_square = self.squares[rand_pos_debug[0].y // self.Ytl][rand_pos_debug[0].x // self.Xtl]
                move = rand_pos_debug[1]
                piece_id = rand_pos_debug[0].id
                if self.new_game_state(self.GRID, origin_square, move, piece_id):
                    return True

            elif self.black_AI and not self.white_turn:
                print('\nBLACK IS CHOOSING A MOVE\n')
                # origin_square, move, piece_id = self.black_bot.generate_move(self.squares, self.GRID, self.white_pieces, self.black_pieces)
                rand_pos_debug = random.choice(list(self.position.children.values()))
                origin_square = self.squares[rand_pos_debug[0].y // self.Ytl][rand_pos_debug[0].x // self.Xtl]
                move = rand_pos_debug[1]
                piece_id = rand_pos_debug[0].id
                if self.new_game_state(self.GRID, origin_square, move, piece_id):
                    return True
                
# i hear voices in the walls......

def main():

    game = Game()
    if game.start():
        main()  # lol

if __name__ == '__main__':
    main()
