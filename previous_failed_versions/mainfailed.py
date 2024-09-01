"""
Ideas:
- for each move, make a grid copy and make a list of pieces based on that copy. check if the king is in check using the classes in the list



"""

import pygame
from Chess.previous_failed_versions.piecesfailed import King, Queen, Pawn, Bishop, Knight, Rook
import sys

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

        self.colour = self.game.cl[colour]
        self.normal_colour = self.colour
        self.clicked = False

        self.piece = None

    def __repr__(self):
        x = self.x // self.game.Xtl
        y = self.y // self.game.Ytl
        return f'{x, y}'

    def draw(self):
        pygame.draw.rect(self.game.display, self.colour, pygame.Rect(self.x, self.y, self.game.Xtl, self.game.Ytl))

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
            'dg': (96, 96, 96)
        }

        self.clock = pygame.time.Clock()
        self.FPS = 60

        self.run = False
        self.whites_turn = True
        self.spritesheet = Spritesheet('img/spritesheet.png')

        self.grid = [ # first letter is colour, second is piece in chess notation, 00 is empty
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr'],
        ]

        self.GRID = None

        self.testing_grid = [  # TESTING ONLY
            ['wk', '00', '00', '00', '00', '00', 'bq', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', 'wq', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', 'bk'],
        ]

        self.squares = []

        self.white_pieces = []
        self.black_pieces = []

        self.squares_to_move = []
        self.selected_square = None

        self.white_turn = True
        self.move_number = 0

    def mk_pieces(self, piece, x, y, square):

        if piece == 'br':
            square.piece = Rook(self, x, y, piece[0], piece)
            self.black_pieces.append(square.piece)

        if piece == 'bn':
            square.piece = Knight(self, x, y, piece[0], piece)
            self.black_pieces.append(square.piece)

        if piece == 'bb':
            square.piece = Bishop(self, x, y, piece[0], piece)
            self.black_pieces.append(square.piece)

        if piece == 'bq':
            square.piece = Queen(self, x, y, piece[0], piece)
            self.black_pieces.append(square.piece)

        if piece == 'bk':
            square.piece = King(self, x, y, piece[0], piece)
            self.black_pieces.append(square.piece)

        if piece == 'bp':
            square.piece = Pawn(self, x, y, piece[0], piece)
            self.black_pieces.append(square.piece)

        if piece == 'wp':
            square.piece = Pawn(self, x, y, piece[0], piece)
            self.white_pieces.append(square.piece)

        if piece == 'wr':
            square.piece = Rook(self, x, y, piece[0], piece)
            self.white_pieces.append(square.piece)

        if piece == 'wn':
            square.piece = Knight(self, x, y, piece[0], piece)
            self.white_pieces.append(square.piece)

        if piece == 'wb':
            square.piece = Bishop(self, x, y, piece[0], piece)
            self.white_pieces.append(square.piece)

        if piece == 'wq':
            square.piece = Queen(self, x, y, piece[0], piece)
            self.white_pieces.append(square.piece)

        if piece == 'wk':
            square.piece = King(self, x, y, piece[0], piece)
            self.white_pieces.append(square.piece)


    def create_grid(self, grid):
        self.white_pieces = []
        self.black_pieces = []

        self.squares = []
        self.GRID = grid # for testing grids
        for i, row in enumerate(self.GRID): # TESTING GRIDS HERE
            a = []
            for j, col in enumerate(row):
                if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                    square = Square(self, j, i, 'w')
                    a.append(square)

                else:
                    square = Square(self, j, i, 'g')
                    a.append(square)

                self.mk_pieces(self.GRID[i][j], j, i, square) # TESTING GRIDS HERE

            self.squares.append(a)

    def new_grid(self, origin, target, piece, check=False):

        """make a sim function: get pos of pieces if a move was to be made, if king is still attacked, return false. do this in the in_check method"""
        copy = self.GRID
        x1, y1 = origin
        x2, y2 = target
        copy[y1][x1] = '00'
        copy[y2][x2] = piece

        temp_black = self.black_pieces
        temp_white = self.white_pieces

        self.create_grid(copy)

    def king_in_check(self, piece, move):
        colour = piece.colour
        grid = self.GRID
        x1, y1 = piece.x // self.Xtl, piece.y // self.Ytl
        x2, y2 = move.x // self.Xtl, move.y // self.Ytl
        grid[y1][x1] = '00'
        grid[y2][x2] = piece

        temp_black = self.black_pieces
        temp_white = self.white_pieces

        self.create_grid(grid)

        if piece.colour == 'w':
            for p in self.white_pieces:
                m = p.valid_moves()
                for k in self.white_pieces:
                    if k.colour == 'w' and k.class_value == 'king':
                        king = k

                if (king.x // self.Xtl, king.y // self.Ytl) in m:
                    self.black_pieces = temp_black
                    self.white_pieces = temp_white
                    return True
        else:
            for p in self.black_pieces:
                m = p.valid_moves()
                for k in self.black_pieces:
                    if k.colour == 'b' and k.class_value == 'king':
                        king = k
                        
                if (king.x // self.Xtl, king.y // self.Ytl) in m:
                    self.black_pieces = temp_black
                    self.white_pieces = temp_white
                    return True
        return False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                pygame.quit()
                sys.exit()

            if pygame.mouse.get_pressed()[0]: # This is an absolute fucking mess of code

                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]

                x //= self.Xtl
                y //= self.Ytl

                # px, py = x * self.Xtl, y * self.Ytl # for white/black pieces list

                s = self.squares[y][x]
                if s.piece != None:
                    is_piece = True
                    piece = s.piece
                else:
                    is_piece = False

                if s not in self.squares_to_move and is_piece:

                    if not self.squares_to_move == []:
                        for i in self.squares_to_move:
                            i.clicked = False
                        self.squares_to_move = []

                    self.selected_square = s

                    s.clicked = True
                    self.squares_to_move.append(s) # moves will be added here later

                    if (piece.colour == 'w' and self.white_turn) or (piece.colour == 'b' and not self.white_turn):
                        moves = piece.valid_moves()
                        if moves == "Stalemate":
                            print("STALEMATE")

                        for move in moves:
                            if self.king_in_check(piece, move) == True:
                                moves.remove(move)

                            move.clicked = True
                            self.squares_to_move.append(move)

                elif s in self.squares_to_move:
                    if s != self.selected_square:
                        self.new_grid((self.selected_square.piece.x // self.Xtl, self.selected_square.piece.y // self.Ytl), (x, y), self.selected_square.piece.id)

                        self.selected_square.piece.x, self.selected_square.piece.y = s.x, s.y

                        s.piece = self.selected_square.piece # s is the new square that the piece moves to

                        self.selected_square.piece = None
                        self.selected_square = None

                        self.move_number += 1
                        if self.white_turn:
                            self.white_turn = False
                        else:
                            self.white_turn = True

                    for i in self.squares_to_move:
                        i.clicked = False

                    self.squares_to_move = []

                else:
                    for i in self.squares_to_move:
                        i.clicked = False
                    self.squares_to_move = []

    def update(self):
        self.display.fill(self.cl['b'])

        for i in self.squares:
            for j in i:

                if j.clicked:
                    j.colour = self.cl['dg']
                else:
                    j.colour = j.normal_colour

                j.draw()

                if j.piece != None:
                    j.piece.draw()

        pygame.display.update()

    def start(self):
        self.create_grid(self.testing_grid)

        self.run = True

        while self.run:
            self.clock.tick(self.FPS)
            self.events()
            self.update()


def main():
    game = Game()
    game.start()

if __name__ == '__main__':
    main()
