"""
optimization ideas:
- maybe just abandon the square class for searches altogether, and use only the grid?
--> this would require some benchmarking and research

- use magic bitboards for sliding pieces
- would compiling the program help?
"""

class Pawn:

    class_value = 'pawn'
    worth = 100

    def __init__(self, game, position, x, y, colour, piece_id, grid):
        self.id = piece_id
        self.game = game
        self.position = position
        self.colour = colour
        self.yx_pos = (y, x)  # y, x for squares indexes
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.grid = grid

        self.enpassant = False

        self.image = self.game.graphics[piece_id]

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False, norecursion=False): # need to add en passant and promotions
        all_moves = []

        square = squares_array

        j, i = self.yx_pos # grid checks y, then x, hence [j] then [i]

        if self.colour == 'w':

            if j > 0 and square[j - 1][i].piece == None:
                all_moves.append(square[j - 1][i])  # TEMPORARY FOR DEBUG
                if j == 6 and square[j - 2][i].piece == None:
                    all_moves.append(square[j - 2][i])

            # capturing
            if (j > 0 and i > 0 and square[j - 1][i - 1].piece != None and square[j - 1][i - 1].piece.colour == 'b') or (j == 3 and i > 0 and (square[j][i - 1].piece != None and square[j][i - 1].piece.class_value == 'pawn' and square[j][i - 1].piece.enpassant == True)):
                all_moves.append(square[j - 1][i - 1])

            if (j > 0 and i < 7 and square[j - 1][i + 1].piece != None and square[j - 1][i + 1].piece.colour == 'b') or (j == 3 and i < 7 and (square[j][i + 1].piece != None and square[j][i + 1].piece.class_value == 'pawn' and square[j][i + 1].piece.enpassant == True)):
                all_moves.append(square[j - 1][i + 1])

        elif self.colour == 'b':

            if j < 7 and square[j + 1][i].piece == None:
                all_moves.append(square[j + 1][i])
                if j == 1 and square[j + 2][i].piece == None:
                    all_moves.append(square[j + 2][i])

            if (j < 7 and i > 0 and square[j + 1][i - 1].piece != None and square[j + 1][i - 1].piece.colour == 'w') or (j == 4 and i > 0 and (square[j][i - 1].piece != None and square[j][i - 1].piece.class_value == 'pawn' and square[j][i - 1].piece.enpassant == True)):
                all_moves.append(square[j + 1][i - 1])

            if (j < 7 and i < 7 and square[j + 1][i + 1].piece != None and square[j + 1][i + 1].piece.colour == 'w') or (j == 4 and i < 7 and (square[j][i + 1].piece != None and square[j][i + 1].piece.class_value == 'pawn' and square[j][i + 1].piece.enpassant == True)):
                all_moves.append(square[j + 1][i + 1])

        # if cull_illegal_moves:
        if not norecursion:
            bad_moves = self.position.illegal_moves(self.grid, all_moves, square[j][i])
        else:
            bad_moves = None
            # for move in bad_moves:
            #     all_moves.remove(move)

        return all_moves, bad_moves

    def __repr__(self):
        return f'[{self.class_value}; y, x: {(self.y//self.position.Ytl, self.x//self.position.Xtl)}; EN PASSANT: {self.enpassant}]'

class King:

    class_value = 'king'
    worth = 0  # this value will always cancel with the other king unless something has gone very wrong

    def __init__(self, game, position, x, y, colour,piece_id, grid):
        self.id = piece_id
        self.game = game
        self.position = position
        self.colour = colour
        self.yx_pos = (y, x)  # y, x for squares indexes
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.grid = grid

        
        self.image = self.game.graphics[piece_id]

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False, add_castling=False, norecursion=False):
        all_moves = []

        square = squares_array

        j, i = self.yx_pos # grid checks y, then x, hence [j] then [i]

        if i > 0:
            s = square[j][i - 1] # s is the tile on the board --> class object
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)

        if i < 7:
            s = square[j][i + 1]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)

        if j > 0:
            s = square[j - 1][i]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)

        if j < 7:
            s = square[j + 1][i]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
        # diagonals
        if i > 0 and j > 0:
            s = square[j - 1][i - 1]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)

        if i > 0 and j < 7:
            s = square[j + 1][i - 1]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)

        if i < 7 and j > 0:
            s = square[j - 1][i + 1]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)

        if i < 7 and j < 7:
            s = square[j + 1][i + 1]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)

        # if cull_illegal_moves:
        if not norecursion:
            bad_moves = self.position.illegal_moves(self.grid, all_moves, square[j][i])
        else:
            bad_moves = None
            # for move in bad_moves:
            #     all_moves.remove(move)

        if add_castling:
            if self.position.check_castling(square, longue=True):
                all_moves.append(square[j][i - 2])

            if self.position.check_castling(square, short=True):
                all_moves.append(square[j][i + 2])

        return all_moves, bad_moves # returns a list of objects

    def __repr__(self):
        return f'[{self.class_value}; y, x: {(self.y//self.position.Ytl, self.x//self.position.Xtl)}]'

class Queen:

    class_value = 'queen'
    worth = 900

    def __init__(self, game, position, x, y, colour, piece_id, grid):
        self.id = piece_id
        self.game = game
        self.position = position
        self.colour = colour
        self.yx_pos = (y, x)  # y, x for squares indexes
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.grid = grid

        self.image = self.game.graphics[piece_id]

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False, norecursion=False): # copy and pasted from rook and bishop classes
        all_moves = []

        square = squares_array

        j, i = self.yx_pos

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
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, sw):
            s = square[j + iterator][i - iterator]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, ne):
            s = square[j - iterator][i + iterator]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, se):
            s = square[j + iterator][i + iterator]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_right): # FIX THESE
            s = square[j][i + iterator]

            if s.piece == None:
                all_moves.append(s)

            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_left):
            s = square[j][i - iterator]

            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_up):
            s = square[j - iterator][i]

            if s.piece == None:
                all_moves.append(s)

            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_down):
            s = square[j + iterator][i]

            if s.piece == None:
                all_moves.append(s)

            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        # if cull_illegal_moves:
        if not norecursion:
            bad_moves = self.position.illegal_moves(self.grid, all_moves, square[j][i])
        else:
            bad_moves = None
            # for move in bad_moves:
                # all_moves.remove(move)

        return all_moves, bad_moves

    def __repr__(self):
        return f'[{self.class_value}; y, x: {(self.y//self.position.Ytl, self.x//self.position.Xtl)}]'

class Rook:

    class_value = 'rook'
    worth = 500

    def __init__(self, game, position, x, y, colour, piece_id, grid):
        self.id = piece_id
        self.game = game
        self.position = position
        self.colour = colour
        self.yx_pos = (y, x)  # y, x for squares indexes
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.grid = grid

        self.image = self.game.graphics[piece_id]

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False, norecursion=False):
        all_moves = []

        square = squares_array

        j, i = self.yx_pos

        to_right = 8 - i
        to_left = 1 + i
        to_up = 1 + j
        to_down = 8 - j

        for iterator in range(1, to_right): # FIX THESE
            s = square[j][i + iterator]

            if s.piece == None:
                all_moves.append(s)

            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_left):
            s = square[j][i - iterator]

            if s.piece == None:
                all_moves.append(s)

            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_up):
            s = square[j - iterator][i]

            if s.piece == None:
                all_moves.append(s)

            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, to_down):
            s = square[j + iterator][i]

            if s.piece == None:
                all_moves.append(s)

            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        # if cull_illegal_moves:
        if not norecursion:
            bad_moves = self.position.illegal_moves(self.grid, all_moves, square[j][i])
        else:
            bad_moves = None
            # for move in bad_moves:
            #     all_moves.remove(move)

        return all_moves, bad_moves

    def __repr__(self):
        return f'[{self.class_value}; y, x: {(self.y//self.position.Ytl, self.x//self.position.Xtl)}]'

class Knight:

    class_value = 'knight'
    worth = 300

    def __init__(self, game, position, x, y, colour, piece_id, grid):
        self.id = piece_id
        self.game = game
        self.position = position
        self.colour = colour
        self.yx_pos = (y, x)  # y, x for squares indexes
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.grid = grid

        self.image = self.game.graphics[piece_id]

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False, norecursion=False):
        all_moves = []

        square = squares_array

        j, i = self.yx_pos

        if j > 1 and i > 0:
            s = square[j - 2][i - 1] # super top left
            if s.piece == None:
                all_moves.append(square[j - 2][i - 1])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        if j > 1 and i < 7:
            s = square[j - 2][i + 1] # super top right
            if s.piece == None:
                all_moves.append(square[j - 2][i + 1])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        if j < 6 and i > 0:
            s = square[j + 2][i - 1] # super bottom left
            if s.piece == None:
                all_moves.append(square[j + 2][i - 1])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        if j < 6 and i < 7:
            s = square[j + 2][i + 1] # super bottom right
            if s.piece == None:
                all_moves.append(square[j + 2][i + 1])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        # Flip sides - 'flip' because values invert in relation to the above
        if j > 0 and i > 1:
            s = square[j - 1][i - 2] # flip top left
            if s.piece == None:
                all_moves.append(square[j - 1][i - 2])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        if j > 0 and i < 6:
            s = square[j - 1][i + 2] # flip top right
            if s.piece == None:
                all_moves.append(square[j - 1][i + 2])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        if j < 7 and i > 1:
            s = square[j + 1][i - 2] # flip bottom left
            if s.piece == None:
                all_moves.append(square[j + 1][i - 2])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        if j < 7 and i < 6:
            s = square[j + 1][i + 2] # flip bottom right
            if s.piece == None:
                all_moves.append(square[j + 1][i + 2])
            elif s.piece.colour != self.colour:
                    all_moves.append(s)

        # if cull_illegal_moves:
        if not norecursion:
            bad_moves = self.position.illegal_moves(self.grid, all_moves, square[j][i])
        else:
            bad_moves = None
            # for move in bad_moves:
            #     all_moves.remove(move)

        return all_moves, bad_moves

    def __repr__(self):
        return f'[{self.class_value}; y, x: {(self.y//self.position.Ytl, self.x//self.position.Xtl)}]'

class Bishop:

    class_value = 'bishop'
    worth = 300

    def __init__(self, game, position, x, y, colour, piece_id, grid):
        self.id = piece_id
        self.game = game
        self.position = position
        self.colour = colour
        self.yx_pos = (y, x)  # y, x for squares indexes
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        self.grid = grid

        self.image = self.game.graphics[piece_id]

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self, squares_array, cull_illegal_moves=False, norecursion=False):
        all_moves = []

        square = squares_array

        j, i = self.yx_pos

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
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, sw):
            s = square[j + iterator][i - iterator]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, ne):
            s = square[j - iterator][i + iterator]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break

        for iterator in range(1, se):
            s = square[j + iterator][i + iterator]
            if s.piece == None:
                all_moves.append(s)
            elif s.piece.colour != self.colour:
                all_moves.append(s)
                break
            elif s.piece.colour == self.colour:
                break
        
        # if cull_illegal_moves:
        if not norecursion:
            bad_moves = self.position.illegal_moves(self.grid, all_moves, square[j][i])
        else:
            bad_moves = None
            # for move in bad_moves:
            #     all_moves.remove(move)

        return all_moves, bad_moves

    def __repr__(self):
        return f'[{self.class_value}; y, x: {(self.y//self.position.Ytl, self.x//self.position.Xtl)}]'
