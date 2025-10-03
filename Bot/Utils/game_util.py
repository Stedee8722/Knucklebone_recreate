import random, uuid, json

NUMBER_OF_PLAYERS = 2
NUMBER_OF_COLUMNS = 3
NUMBER_OF_DICES_PER_COLUMN = 3
NUMBER_OF_SIDES_PER_DICE = 6
SAVE_FILE = "Data/game_data.json"

class KnuckleboneGame:
    def __init__(self, player_one_id: int, player_two_id: int):
        self.boards = [
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],  # Player 1's board
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]]   # Player 2's board
        ]
        self.isGameOver = False
        self.current_player = random.randint(0, 1)  # Random player starts
        self.uuid = uuid.uuid4()
        self.player_one_id = player_one_id
        self.player_two_id = player_two_id
        self.dice = 0
        self.turn_history = {
            "board_one": [],
            "board_two": []
        }  # To keep track of turns

    def next_turn(self) -> None:
        self.current_player = NUMBER_OF_PLAYERS - 1 - self.current_player
        self.roll_dice()
    
    def roll_dice(self) -> int:
        self.dice = random.randint(1, 6)
        return self.dice
    
    def check_input(self, input: int, amount: int, from_zero: bool = True) -> int:
        if not from_zero:
            if isinstance(input, int) and 0 < input <= amount:
                return input
            else:
                raise ValueError("Input must be an integer between 1 and " + str(amount) + ". You provided: " + str(input))
        else:
            if isinstance(input, int) and 0 <= input < amount:
                return input
            else:
                raise ValueError("Input must be an integer between 0 and " + str(amount - 1) + ". You provided: " + str(input))
    
    def check_column_space(self, board_num: int, column: int) -> bool:
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        self.check_input(column, NUMBER_OF_COLUMNS)
        board = self.boards[board_num]
        column_data = board[column]
        return 0 in column_data
    
    def place_dice(self, board_num: int, column: int) -> None:
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        self.check_input(column, NUMBER_OF_COLUMNS)
        self.check_input(self.dice, NUMBER_OF_SIDES_PER_DICE, from_zero=False)
        board = self.boards[board_num]
        column_data = board[column]
        for i in range(len(column_data)):
            if column_data[i] == 0:
                column_data[i] = self.dice
                break
        self.save_turn_history(board_num, column, self.dice)
        self.check_clash(board_num, column, self.dice)
        self.move_dice_down()

    def save_turn_history(self, board_num: int, column: int) -> None:
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        if board_num == 0:
            self.turn_history["board_one"].append({"column": column, "dice": self.dice})
        elif board_num == 1:
            self.turn_history["board_two"].append({"column": column, "dice": self.dice})

    def check_clash(self, board_num: int, column: int) -> None:
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        self.check_input(column, NUMBER_OF_COLUMNS)
        self.check_input(self.dice, NUMBER_OF_SIDES_PER_DICE, from_zero=False)
        board = self.boards[board_num]
        column_data = board[column]
        for i in range(len(column_data)):
            if column_data[i] == self.dice:
                column_data[i] = 0

    def calc_total(self, board_num: int) -> int:
        total = 0
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        for i in range(3):
            total += self.calc_column_total(board_num, i)
        return total
        
    def calc_column_total(self, board_num: int, column: int) -> int:
        total = 0
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        self.check_input(column, NUMBER_OF_COLUMNS)
        board = self.boards[board_num]
        column_data = board[column]
        unique_values = set(column_data) - {0}
        for value in unique_values:
            count = column_data.count(value)
            total += value * (count ** 2)
        return total
    
    def move_dice_down(self) -> None:
        for board in self.boards:
            for column in board:
                for i in range(0, 2):
                    if column[i] == 0 and column[i + 1] != 0:
                        column[i] = column[i + 1]
                        column[i + 1] = 0

    def check_game_over(self) -> int:
        for board in self.boards:
            for column in board:
                if 0 in column:
                    return False
        self.isGameOver = True
        return self.get_winner(self)
    
    def get_winner(self) -> int:
        if not self.isGameOver:
            return -1
        score_one = self.calc_total(0)
        score_two = self.calc_total(1)
        if score_one > score_two:
            return 0
        elif score_two > score_one:
            return 1
        else:
            return 2  # Tie

    def get_board(self, board_num: int):
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        return self.boards[board_num]
    
    @classmethod
    def get_game_state(self):
        return self.to_dict(self)
    
    # ---------------- SAVE / LOAD ----------------
    def to_dict(self):
        return {
            "uuid": str(self.uuid),
            "boards": self.boards,
            "isGameOver": self.isGameOver,
            "current_player": self.current_player,
            "player_one_id": self.player_one_id,
            "player_two_id": self.player_two_id,
            "turn_history": self.turn_history,
            "dice": self.dice
        }

    def from_dict(self, data: dict):
        game = self(data["player_one_id"], data["player_two_id"])
        game.uuid = uuid.UUID(data["uuid"])
        game.boards = data["boards"]
        game.isGameOver = data["isGameOver"]
        game.current_player = data["current_player"]
        game.turn_history = data["turn_history"]
        game.dice = data["dice"]
        return game

    @staticmethod
    async def save(self):
        """Save the current game state to a file."""
        import os
        if not os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "w") as f:
                json.dump({}, f)

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        data[str(self.uuid)] = self.to_dict()

        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load(self, game_id: str):
        """Load game by id from the save file."""
        import json, os
        if not os.path.exists(SAVE_FILE):
            return None

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        if game_id not in data:
            return None

        return self.from_dict(data[game_id])