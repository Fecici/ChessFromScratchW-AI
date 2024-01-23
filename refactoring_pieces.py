class Pawn:

    class_value = 'pawn'
    worth = 1

    def __init__(self, game, x, y, colour, piece_id):
        self.id = piece_id
        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.enpassant = False

        if self.colour == 'w':
            self.image = self.game.spritesheet.get_sprite(120 * 9, 0, self.game.Xtl, self.game.Ytl) # x val of get_sprite() is multiplied by the image's place in the sequence on the spritesheet, starting from 0
        else:
            self.image = self.game.spritesheet.get_sprite(120 * 3, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False): # need to add en passant and promotions
        legal_moves = []

        square = squares_array

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl # grid checks y, then x, hence [j] then [i]

        if self.colour == 'w':

            if j > 0 and square[j - 1][i].piece == None:
                legal_moves.append(square[j - 1][i])
                if j == 6 and square[j - 2][i].piece == None:
                    legal_moves.append(square[j - 2][i])

            # capturing
            if (j > 0 and i > 0 and square[j - 1][i - 1].piece != None and square[j - 1][i - 1].piece.colour == 'b') or (j == 3 and i > 0 and (square[j][i - 1].piece != None and square[j][i - 1].piece.class_value == 'pawn' and square[j][i - 1].piece.enpassant == True)):
                legal_moves.append(square[j - 1][i - 1])

            if (j > 0 and i < 7 and square[j - 1][i + 1].piece != None and square[j - 1][i + 1].piece.colour == 'b') or (j == 3 and i < 7 and (square[j][i + 1].piece != None and square[j][i + 1].piece.class_value == 'pawn' and square[j][i + 1].piece.enpassant == True)):
                legal_moves.append(square[j - 1][i + 1])

        elif self.colour == 'b':

            if j < 7 and square[j + 1][i].piece == None:
                legal_moves.append(square[j + 1][i])
                if j == 1 and square[j + 2][i].piece == None:
                    legal_moves.append(square[j + 2][i])

            if (j < 7 and i > 0 and square[j + 1][i - 1].piece != None and square[j + 1][i - 1].piece.colour == 'w') or (j == 4 and i > 0 and (square[j][i - 1].piece != None and square[j][i - 1].piece.class_value == 'pawn' and square[j][i - 1].piece.enpassant == True)):
                legal_moves.append(square[j + 1][i - 1])

            if (j < 7 and i < 7 and square[j + 1][i + 1].piece != None and square[j + 1][i + 1].piece.colour == 'w') or (j == 4 and i < 7 and (square[j][i + 1].piece != None and square[j][i + 1].piece.class_value == 'pawn' and square[j][i + 1].piece.enpassant == True)):
                legal_moves.append(square[j + 1][i + 1])

        if cull_illegal_moves:
            bad_moves = self.game.illegal_moves(legal_moves, square[j][i])
            for move in bad_moves:
                legal_moves.remove(move)

        return legal_moves

    def __repr__(self):
        return f'{self.class_value}, {(self.x//self.game.Xtl, self.y//self.game.Ytl)}'

class King:

    class_value = 'king'
    worth = 0  # this value will always cancel with the other king unless something has gone very wrong

    def __init__(self, game, x, y, colour,piece_id):
        self.id = piece_id
        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        
        if self.colour == 'w':

            self.castling_short, self.castling_long = self.game.king_castle_short_white, self.game.king_castle_long_white
            self.image = self.game.spritesheet.get_sprite(120 * 7, 0, self.game.Xtl, self.game.Ytl)

        else:
            self.castling_short, self.castling_long = self.game.king_castle_short_black, self.game.king_castle_long_black
            self.image = self.game.spritesheet.get_sprite(120, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False, add_castling=False):
        legal_moves = []

        square = squares_array

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl # grid checks y, then x, hence [j] then [i]

        if i > 0:
            s = square[j][i - 1] # s is the tile on the board --> class object
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)

        if i < 7:
            s = square[j][i + 1]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)

        if j > 0:
            s = square[j - 1][i]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)

        if j < 7:
            s = square[j + 1][i]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
        # diagonals
        if i > 0 and j > 0:
            s = square[j - 1][i - 1]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)

        if i > 0 and j < 7:
            s = square[j + 1][i - 1]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)

        if i < 7 and j > 0:
            s = square[j - 1][i + 1]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)

        if i < 7 and j < 7:
            s = square[j + 1][i + 1]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)

        if cull_illegal_moves:
            bad_moves = self.game.illegal_moves(legal_moves, square[j][i])
            for move in bad_moves:
                legal_moves.remove(move)

        if add_castling:
            if self.game.check_castling(square, self.game.white_pieces, self.game.black_pieces, longue=True):
                legal_moves.append(square[j][i - 2])

            if self.game.check_castling(square, self.game.white_pieces, self.game.black_pieces, short=True):
                legal_moves.append(square[j][i + 2])

        return legal_moves # returns a list of objects

    def __repr__(self):
        return f'{self.class_value}, {(self.x//self.game.Xtl, self.y//self.game.Ytl)}'

class Queen:

    class_value = 'queen'
    worth = 9

    def __init__(self, game, x, y, colour, piece_id):
        self.id = piece_id
        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        if self.colour == 'w':
            self.image = self.game.spritesheet.get_sprite(120 * 10, 0, self.game.Xtl, self.game.Ytl)
        else:
            self.image = self.game.spritesheet.get_sprite(120 * 4, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False): # copy and pasted from rook and bishop classes
        legal_moves = []

        square = squares_array

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl

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
            s = square[j - iterator][i - iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, sw):
            s = square[j + iterator][i - iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, ne):
            s = square[j - iterator][i + iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, se):
            s = square[j + iterator][i + iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_right): # FIX THESE
            s = square[j][i + iterator]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_left):
            s = square[j][i - iterator]

            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_up):
            s = square[j - iterator][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_down):
            s = square[j + iterator][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        if cull_illegal_moves:
            bad_moves = self.game.illegal_moves(legal_moves, square[j][i])
            for move in bad_moves:
                legal_moves.remove(move)

        return legal_moves

    def __repr__(self):
        return f'{self.class_value}, {(self.x//self.game.Xtl, self.y//self.game.Ytl)}'

class Rook:

    class_value = 'rook'
    worth = 5

    def __init__(self, game, x, y, colour, piece_id):
        self.id = piece_id
        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        if self.colour == 'w':
            self.image = self.game.spritesheet.get_sprite(120 * 11, 0, self.game.Xtl, self.game.Ytl)

        else:
            self.image = self.game.spritesheet.get_sprite(120 * 5, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False):
        legal_moves = []

        square = squares_array

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl

        to_right = 8 - i
        to_left = 1 + i
        to_up = 1 + j
        to_down = 8 - j

        for iterator in range(1, to_right): # FIX THESE
            s = square[j][i + iterator]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_left):
            s = square[j][i - iterator]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_up):
            s = square[j - iterator][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_down):
            s = square[j + iterator][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        if cull_illegal_moves:
            bad_moves = self.game.illegal_moves(legal_moves, square[j][i])
            for move in bad_moves:
                legal_moves.remove(move)

        return legal_moves

    def __repr__(self):
        return f'{self.class_value}, {(self.x//self.game.Xtl, self.y//self.game.Ytl)}'

class Knight:

    class_value = 'knight'
    worth = 3

    def __init__(self, game, x, y, colour, piece_id):
        self.id = piece_id
        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        if self.colour == 'w':
            self.image = self.game.spritesheet.get_sprite(120 * 8, 0, self.game.Xtl, self.game.Ytl)
        else:
            self.image = self.game.spritesheet.get_sprite(120 * 2, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False):
        legal_moves = []

        square = squares_array

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl

        if j > 1 and i > 0:
            s = square[j - 2][i - 1] # super top left
            if s.piece == None:
                legal_moves.append(square[j - 2][i - 1])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j > 1 and i < 7:
            s = square[j - 2][i + 1] # super top right
            if s.piece == None:
                legal_moves.append(square[j - 2][i + 1])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 6 and i > 0:
            s = square[j + 2][i - 1] # super bottom left
            if s.piece == None:
                legal_moves.append(square[j + 2][i - 1])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 6 and i < 7:
            s = square[j + 2][i + 1] # super bottom right
            if s.piece == None:
                legal_moves.append(square[j + 2][i + 1])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        # Flip sides - 'flip' because values invert in relation to the above
        if j > 0 and i > 1:
            s = square[j - 1][i - 2] # flip top left
            if s.piece == None:
                legal_moves.append(square[j - 1][i - 2])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j > 0 and i < 6:
            s = square[j - 1][i + 2] # flip top right
            if s.piece == None:
                legal_moves.append(square[j - 1][i + 2])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 7 and i > 1:
            s = square[j + 1][i - 2] # flip bottom left
            if s.piece == None:
                legal_moves.append(square[j + 1][i - 2])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 7 and i < 6:
            s = square[j + 1][i + 2] # flip bottom right
            if s.piece == None:
                legal_moves.append(square[j + 1][i + 2])
            elif s.piece.colour != self.colour:
                    legal_moves.append(s)

        if cull_illegal_moves:
            bad_moves = self.game.illegal_moves(legal_moves, square[j][i])
            for move in bad_moves:
                legal_moves.remove(move)

        return legal_moves

    def __repr__(self):
        return f'{self.class_value}, {(self.x//self.game.Xtl, self.y//self.game.Ytl)}'

class Bishop:

    class_value = 'bishop'
    worth = 3

    def __init__(self, game, x, y, colour, piece_id):
        self.id = piece_id
        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        if self.colour == 'w':
            self.image = self.game.spritesheet.get_sprite(120 * 6, 0, self.game.Xtl, self.game.Ytl)
        else:
            self.image = self.game.spritesheet.get_sprite(120 * 0, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False):
        legal_moves = []

        square = squares_array

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl

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
            s = square[j - iterator][i - iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, sw):
            s = square[j + iterator][i - iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, ne):
            s = square[j - iterator][i + iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, se):
            s = square[j + iterator][i + iterator]
            if s.piece == None:
                legal_moves.append(s)
            elif s.piece.colour != self.colour:
                legal_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break
        
        if cull_illegal_moves:
            bad_moves = self.game.illegal_moves(legal_moves, square[j][i])
            for move in bad_moves:
                legal_moves.remove(move)

        return legal_moves

    def __repr__(self):
        return f'{self.class_value}, {(self.x//self.game.Xtl, self.y//self.game.Ytl)}'
