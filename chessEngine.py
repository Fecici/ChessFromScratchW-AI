import random

class ChessEngine:
    def __init__(self, game, colour) -> None:
        self.game = game
        self.colour = colour  # i am not sure yet if i am going to use this attribute

        # these values will influence which moves the computer will prioritize
        self.white_pawn_positions = [
            [9, 9, 9, 9, 9, 9, 9, 9],
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
                        white_score += square.piece.worth + 1  # idk why im adding 1, its really just arbitrary
                        
                    elif square.piece.colour == 'b':
                        black_score += square.piece.worth + 1

        return white_score, black_score

    def evaluate_position(self, board, move, depth=1):
        """
        This method will be run on all available moves.

        perhaps the yield keyword might be of use here when the depth is implemented.

        currently, the "future" variables are slightly misleading, as
        all future positions are generated in the generate_move() method.
        should probably rename the variables to "current" state for better
        readability
        """

        origin_square = board[move[0].y // self.game.Ytl][move[0].x // self.game.Xtl]
        move_pos = move[1].pos

        grade = 0

        board_state = self.game.new_move(origin_square.pos, move_pos, origin_square.piece.id)  # maybe i can make a hidden flag for specific bot promotions
        black_pieces, white_pieces, squares_list = self.game.create_grid(board_state)

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
        
        white_position_value, black_position_value = self.apply_piece_map(squares_list, white_pieces, black_pieces, scale=0.5)
        white_score += white_position_value
        black_score += black_position_value

        # for now, this method will only look at material gain.
        # depth will be used later to evaluate future moves in the position
        # as this method technically is being used to check moves with depth 1 anyways
        grade += white_score - black_score
        grade *= random.randint(8, 12) / 10  # lolll, just a bit of randomness to spice things up a bit

        return grade

    def generate_move(self, board, white_pieces, black_pieces):
        """
        this method is only for testing, should be renamed so as to be less ambiguous

        "wahhw, u can really dance :o" - current state of the bot
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
