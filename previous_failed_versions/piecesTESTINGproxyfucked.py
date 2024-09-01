import pygame

class Pawn:

    class_value = 'pawn'

    def __init__(self, game, x, y, colour, id):
        self.id = id

        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        if self.colour == 'w':
            self.image = self.game.spritesheet.get_sprite(120 * 9, 0, self.game.Xtl, self.game.Ytl) # x val of get_sprite() is multiplied by the image's place in the sequence on the spritesheet, starting from 0
        else:
            self.image = self.game.spritesheet.get_sprite(120 * 3, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def valid_moves(self): # need to add en passant and promotions
        legal_moves = []

        square = self.game.squares

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl # grid checks y, then x, hence [j] then [i]

        if self.colour == 'w':

            if j > 0 and square[j - 1][i].piece == None: # and king is not in check
                legal_moves.append(square[j - 1][i])
                if j == 6 and square[j - 2][i].piece == None:
                    legal_moves.append(square[j - 2][i])

            # capturing
            if (j > 0 and i > 0 and square[j - 1][i - 1].piece != None and square[j - 1][i - 1].piece.colour == 'b'):
                legal_moves.append(square[j - 1][i - 1])

            if (j > 0 and i < 7 and square[j - 1][i + 1].piece != None and square[j - 1][i + 1].piece.colour == 'b'):
                legal_moves.append(square[j - 1][i + 1])

        elif self.colour == 'b':

            if j < 7 and square[j + 1][i].piece == None: # and king is not in check
                legal_moves.append(square[j + 1][i])
                if j == 1 and square[j + 2][i].piece == None:
                    legal_moves.append(square[j + 2][i])

            if (j < 7 and i > 0 and square[j + 1][i - 1].piece != None and square[j + 1][i - 1].piece.colour == 'w'):
                legal_moves.append(square[j + 1][i - 1])

            if (j < 7 and i < 7 and square[j + 1][i + 1].piece != None and square[j + 1][i + 1].piece.colour == 'w'):
                legal_moves.append(square[j + 1][i + 1])


        return legal_moves

    def promote(self):
        pass

    def __repr__(self):
        return self.class_value

class King:

    class_value = 'king'

    def __init__(self, game, x, y, colour, id):
        self.id = id

        self.game = game
        self.colour = colour
        self.x = x * self.game.Xtl
        self.y = y * self.game.Ytl

        if self.colour == 'w':
            self.image = self.game.spritesheet.get_sprite(120 * 7, 0, self.game.Xtl, self.game.Ytl)
        else:
            self.image = self.game.spritesheet.get_sprite(120, 0, self.game.Xtl, self.game.Ytl)

    def draw(self):
        self.game.display.blit(self.image, (self.x, self.y))

    def in_check(self): # take all enemy squares and check that the desired move is not in them or that king is not in check during its move
        move = []
        if self.colour == 'w':
            for i in self.game.black_pieces:
                if i.class_value != 'king':
                    bad_squares = i.valid_moves()

                    for i in bad_squares:
                        move.append(i)
                else:
                    bad_squares = i.valid_moves(search=False)
                    for i in bad_squares:
                        move.append(i)

        else:
            for i in self.game.white_pieces:
                if i.class_value != 'king':
                    bad_squares = i.valid_moves()

                    for i in bad_squares:
                        move.append(i)
                else:
                    bad_squares = i.valid_moves(search=False)
                    for i in bad_squares:
                        move.append(i)

        return move

    def valid_moves(self, search=True): # how the fuck does this entire method even work properly?? (it doesnt)
        legal_moves = []

        square = self.game.squares

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl # grid checks y, then x, hence [j] then [i]

        if i > 0:
            s = square[j][i - 1]
            if s.piece == None:
                legal_moves.append(square[j][i - 1])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if i < 7:
            s = square[j][i + 1]
            if s.piece == None:
                legal_moves.append(square[j][i + 1])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j > 0:
            s = square[j - 1][i]
            if s.piece == None:
                legal_moves.append(square[j - 1][i])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 7:
            s = square[j + 1][i]
            if s.piece == None:
                legal_moves.append(square[j + 1][i])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if i > 0 and j > 0:
            s = square[j - 1][i - 1]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if i > 0 and j < 7:
            s = square[j + 1][i - 1]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if i < 7 and j > 0:
            s = square[j - 1][i + 1]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if i < 7 and j < 7:
            s = square[j + 1][i + 1]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if search: #  only for kings
            bad_moves = self.in_check()
            for i in bad_moves:
                if i in legal_moves:
                    legal_moves.remove(i)

        return legal_moves

    def __repr__(self):
        return self.class_value

class Queen:

    class_value = 'queen'

    def __init__(self, game, x, y, colour, id):
        self.id = id

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

    def valid_moves(self): # copy and pasted from rook and bishop classes
        legal_moves = []

        square = self.game.squares

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

        for iter in range(1, nw):
            s = square[j - iter][i - iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, sw):
            s = square[j + iter][i - iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, ne):
            s = square[j - iter][i + iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, se):
            s = square[j + iter][i + iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, to_right): # FIX THESE
            s = square[j][i + iter]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, to_left):
            s = square[j][i - iter]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, to_up):
            s = square[j - iter][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, to_down):
            s = square[j + iter][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        return legal_moves

    def __repr__(self):
        return self.class_value

class Rook:

    class_value = 'rook'

    def __init__(self, game, x, y, colour, id):
        self.id = id

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

    def valid_moves(self):
        legal_moves = []

        square = self.game.squares

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl

        to_right = 8 - i
        to_left = 1 + i
        to_up = 1 + j
        to_down = 8 - j

        for iter in range(1, to_right): # FIX THESE
            s = square[j][i + iter]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, to_left):
            s = square[j][i - iter]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, to_up):
            s = square[j - iter][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, to_down):
            s = square[j + iter][i]

            if s.piece == None:
                legal_moves.append(s)

            elif s.piece != None:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        return legal_moves

    def __repr__(self):
        return self.class_value

class Knight:

    class_value = 'knight'

    def __init__(self, game, x, y, colour, id):
        self.id = id

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

    def valid_moves(self):
        legal_moves = []

        square = self.game.squares

        i, j = self.x // self.game.Xtl, self.y // self.game.Ytl

        if j > 1 and i > 0:
            s = square[j - 2][i - 1] # super top left
            if s.piece == None:
                legal_moves.append(square[j - 2][i - 1])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j > 1 and i < 7:
            s = square[j - 2][i + 1] # super top right
            if s.piece == None:
                legal_moves.append(square[j - 2][i + 1])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 6 and i > 0:
            s = square[j + 2][i - 1] # super bottom left
            if s.piece == None:
                legal_moves.append(square[j + 2][i - 1])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 6 and i < 7:
            s = square[j + 2][i + 1] # super bottom right
            if s.piece == None:
                legal_moves.append(square[j + 2][i + 1])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        # Flip sides - 'flip' because values invert in relation to the above
        if j > 0 and i > 1:
            s = square[j - 1][i - 2] # flip top left
            if s.piece == None:
                legal_moves.append(square[j - 1][i - 2])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j > 0 and i < 6:
            s = square[j - 1][i + 2] # flip top right
            if s.piece == None:
                legal_moves.append(square[j - 1][i + 2])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 7 and i > 1:
            s = square[j + 1][i - 2] # flip bottom left
            if s.piece == None:
                legal_moves.append(square[j + 1][i - 2])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        if j < 7 and i < 6:
            s = square[j + 1][i + 2] # flip bottom right
            if s.piece == None:
                legal_moves.append(square[j + 1][i + 2])
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)

        return legal_moves

    def __repr__(self):
        return self.class_value

class Bishop:

    class_value = 'bishop'

    def __init__(self, game, x, y, colour, id):
        self.id = id

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

    def valid_moves(self):
        legal_moves = []

        square = self.game.squares

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

        for iter in range(1, nw):
            s = square[j - iter][i - iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, sw):
            s = square[j + iter][i - iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, ne):
            s = square[j - iter][i + iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        for iter in range(1, se):
            s = square[j + iter][i + iter]
            if s.piece == None:
                legal_moves.append(s)
            else:
                if s.piece.colour != self.colour:
                    legal_moves.append(s)
                break

        return legal_moves

    def __repr__(self):
        return self.class_value
