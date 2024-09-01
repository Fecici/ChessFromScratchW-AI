"""
Ideas:
- for each move, make a grid copy and make a list of pieces based on that copy. check if the king is in check using the classes in the list
- redo mouse movement and checks


"""

import pygame; import sys; from Chess.previous_failed_versions.REWRITE_PIECES import King, Queen, Pawn, Bishop, Knight, Rook

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

        self.rect = pygame.Rect(self.x, self.y, self.game.Xtl, self.game.Ytl) # square rect, also used for collidepointer()

        self.piece = None # piece stored on square

    def __repr__(self):
        x = self.x // self.game.Xtl
        y = self.y // self.game.Ytl

        if self.piece == None:
            return f'E, {x, y}'
        return f'{self.piece.id, x, y}'

    def draw(self):
        # if self.clicked:
        #     self.colour = self.game.cl['bg'] # change colour to other than dg
        #
        # elif self.legal_move:
        #     self.colour = self.game.cl['dg']
        #
        # else:
        #     self.colour = self.normal_colour

        pygame.draw.rect(self.game.display, self.colour, self.rect)

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
            ['00', '00', 'br', '00', '00', 'bp', '00', '00'],
            ['00', '00', '00', '00', '00', '00', '00', '00'],
            ['00', '00', '00', '00', 'wr', '00', '00', '00'],
            ['00', '00', 'wn', '00', '00', '00', '00', '00'],
            ['00', 'bb', 'wq', '00', '00', '00', 'bn', '00'],
            ['00', 'wb', '00', '00', '00', '00', 'wp', '00'],
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
        black_pieces = []
        white_pieces = []

        if piece == 'br':
            square.piece = Rook(self, x, y, piece[0], piece)
            black_pieces.append(square.piece)

        if piece == 'bn':
            square.piece = Knight(self, x, y, piece[0], piece)
            black_pieces.append(square.piece)

        if piece == 'bb':
            square.piece = Bishop(self, x, y, piece[0], piece)
            black_pieces.append(square.piece)

        if piece == 'bq':
            square.piece = Queen(self, x, y, piece[0], piece)
            black_pieces.append(square.piece)

        if piece == 'bk':
            square.piece = King(self, x, y, piece[0], piece)
            black_pieces.append(square.piece)

        if piece == 'bp':
            square.piece = Pawn(self, x, y, piece[0], piece)
            black_pieces.append(square.piece)

        if piece == 'wp':
            square.piece = Pawn(self, x, y, piece[0], piece)
            white_pieces.append(square.piece)

        if piece == 'wr':
            square.piece = Rook(self, x, y, piece[0], piece)
            white_pieces.append(square.piece)

        if piece == 'wn':
            square.piece = Knight(self, x, y, piece[0], piece)
            white_pieces.append(square.piece)

        if piece == 'wb':
            square.piece = Bishop(self, x, y, piece[0], piece)
            white_pieces.append(square.piece)

        if piece == 'wq':
            square.piece = Queen(self, x, y, piece[0], piece)
            white_pieces.append(square.piece)

        if piece == 'wk':
            square.piece = King(self, x, y, piece[0], piece)
            white_pieces.append(square.piece)

        return black_pieces, white_pieces


    def create_grid(self, grid):

        black_pieces = []
        white_pieces = []

        squares = []
        for i, row in enumerate(grid): # TESTING GRIDS HERE
            a = []
            for j, col in enumerate(row):
                if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                    square = Square(self, j, i, 'w')
                    a.append(square)

                else:
                    square = Square(self, j, i, 'g')
                    a.append(square)

                bl, wh = self.mk_pieces(grid[i][j], j, i, square) # TESTING GRIDS HERE

                if bl != []:
                    d = bl[0]
                    black_pieces.append(d)

                if wh != []:
                    d = wh[0]
                    white_pieces.append(d)

            squares.append(a) # squares is a 2 dimensional list

        return black_pieces, white_pieces, squares

    def new_move(self, origin, target, piece):

        """make a sim function: get pos of pieces if a move was to be made, if king is still attacked, return false. do this in the in_check method"""
        new_grid = self.GRID
        x1, y1 = origin
        x2, y2 = target
        new_grid[y1][x1] = '00'
        new_grid[y2][x2] = piece

        return self.create_grid(new_grid)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN: # test MOUSEBUTTONUP vs MOUSEBUTTONDOWN, main goal is to avoid unintentional spammed button clicks on squares

                pos = pygame.mouse.get_pos()

                for row in self.squares:
                    for square in row:
                        if square.rect.collidepoint(pos):
                            selected_square = square
                            # the logic may be broken here
                            if selected_square != self.selected_square:
                                for lines_persisting in self.squares_to_move: # if i forget why this iter name is funny, just ask jodran
                                    lines_persisting.clicked = False
                                    lines_persisting.legal_move = False
                                self.squares_to_move = []
                                self.selected_square = selected_square
                                print('Got Here 2')

                            else:
                                selected_square.clicked = False
                                for lines_persisting in self.squares_to_move: # if i forget why this iter name is funny, just ask jodran
                                    lines_persisting.clicked = False
                                    lines_persisting.legal_move = False
                                self.squares_to_move = []
                                self.selected_square = None
                                print('Got Here 3')

                            if not selected_square.piece == None:
                                self.squares_to_move = self.check_legal_moves(selected_square)
                                for s in self.squares_to_move:
                                    s.legal_move = True
                                print('Got Here 4')

                # check white's turn after the square is selected

    def check_legal_moves(self, selected_square):
        selected_square.clicked = True
        piece = selected_square.piece

        px, py = piece.x // self.Xtl, piece.y // self.Ytl # piece x, piece y --> used for indexing

        if self.white_turn and piece.colour == 'w':

            for p in self.squares: # p is the list, tem is the square object
                for tem in p:
                    if tem.piece != None and tem.piece.id == 'wk':
                        king = tem

            # kx, ky = king.x // self.Xtl, king.y // self.Ytl # king x, king y --> determine if king is in check

            moves = piece.valid_moves()
            for move in moves:

                mx, my = move.x // self.Xtl, move.y // self.Ytl # --> move x and y for square, not piece. can use same index for what is needed

                bp, _, _, _ = self.new_move((px, py), (mx, my), piece.id)
                for b in bp:
                    """first review king checks, then look at pieces not moving properly"""
                    bad_moves = b.valid_moves()
                    # bad_moves_alpha = []
                    # for bad in bad_moves:
                    #     bad_moves_alpha.append((bad.x//self.Xtl, bad.y//self.Ytl))
                    #
                    # print(f'bad_moves: {bad_moves}, {(king)}\n KING IN MOVES:{king in bad_moves}\n index debug: {moves[0], bad_moves[0]}\n')
                    for jk in bad_moves:
                        if king in bad_moves and move in moves:
                            moves.remove(move)

            return moves

        """
        ******figure out pieces that cannot be captured by king******
        for each piece in enemy pieces:
            check legal moves and store them all in a list
            check if the present move allows the friendly king to be placed in check
            if true, remove the move from squares_to_move if the move is in the list
        """

    def update(self):
        self.display.fill(self.cl['b'])

        for i in self.squares:
            for j in i:

                if j.clicked:
                    j.colour = self.cl['bg'] # change colour to other than dg

                elif j.legal_move:
                    j.colour = self.cl['dg']

                else:
                    j.colour = j.normal_colour

                j.draw()

                if j.piece != None:
                    j.piece.draw()

        pygame.display.update()

    def start(self):
        self.black_pieces, self.white_pieces, self.squares = self.create_grid(self.grid)

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
