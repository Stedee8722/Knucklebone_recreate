import random, uuid, json, discord

NUMBER_OF_PLAYERS = 2
NUMBER_OF_COLUMNS = 3
NUMBER_OF_DICES_PER_COLUMN = 3
NUMBER_OF_SIDES_PER_DICE = 6
SAVE_FILE = "Data/game_data.json"
KNUKLEBONES_EMOJI = "<:knucklebones:1423761306447511552>"
DICE_1_EMOJI = "<:dice_1:1423761282183594246>"
DICE_2_EMOJI = "<:dice_2:1423761286747131904>"
DICE_3_EMOJI = "<:dice_3:1423761292677873724>"
DICE_4_EMOJI = "<:dice_4:1423761295001522198>"
DICE_5_EMOJI = "<:dice_5:1423761297568174101>"
DICE_6_EMOJI = "<:dice_6:1423761301423001630>"

class KnuckleboneGame:
    def __init__(self, player_one_id: int, player_two_id: int):
        self.boards = [
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],  # Player 1's board
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]]   # Player 2's board
        ]
        self.isGameOver = False
        self.current_player = -1  # Random player starts
        self.uuid = uuid.uuid4()
        self.player_one_id = player_one_id
        self.player_two_id = player_two_id
        self.dice = 0
        self.current_turn = 0
        self.turn_history = {
            "board_one": [],
            "board_two": []
        }  # To keep track of turns
        self.winner = -1  # -1 means no winner yet

    def start_game(self) -> None:
        self.current_player = random.randint(0, 1)
        self.current_turn = 1
        self.roll_dice()

    def next_turn(self) -> None:
        self.current_player = 1 - self.current_player
        self.current_turn += 1
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
    
    def check_column_space(self, column: int) -> bool:
        self.check_input(column, NUMBER_OF_COLUMNS)
        board = self.boards[self.current_player]
        column_data = board[column]
        print("Checking column space for column " + str(column) + " on player " + str(self.current_player) + "'s board:")
        print(column_data)
        return 0 in column_data
    
    def place_dice(self, column: int) -> None:
        self.check_input(column, NUMBER_OF_COLUMNS)
        self.check_input(self.dice, NUMBER_OF_SIDES_PER_DICE, from_zero=False)
        for i in range(NUMBER_OF_DICES_PER_COLUMN):
            if self.boards[self.current_player][column][i] == 0:
                self.boards[self.current_player][column][i] = self.dice
                break
        self.save_turn_history(column)
        self.check_clash(column)
        self.check_game_over()
        self.move_dice_down()
        self.save()
        if not self.isGameOver:
            self.next_turn()

    def save_turn_history(self, column: int) -> None:
        if self.current_player == 0:
            self.turn_history["board_one"].append({"column": column, "dice": self.dice, "turn": self.current_turn})
        elif self.current_player == 1:
            self.turn_history["board_two"].append({"column": column, "dice": self.dice, "turn": self.current_turn})

    def check_clash(self, column: int) -> None:
        for i in range(NUMBER_OF_DICES_PER_COLUMN):
            if self.boards[1 - self.current_player][column][i] == self.dice:
                self.boards[1 - self.current_player][column][i] = 0

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
        board = self.boards[self.current_player]
        for column in board:
            if 0 in column:
                return False
        self.isGameOver = True
        return self.get_winner()
    
    def get_winner(self) -> int:
        if self.winner != -1:
            return self.winner
        if not self.isGameOver:
            return -1
        score_one = self.calc_total(0)
        score_two = self.calc_total(1)
        if score_one > score_two:
            self.winner = 0
            return 0
        elif score_two > score_one:
            self.winner = 1
            return 1
        else:
            return 2  # Tie
        
    def resign(self) -> None:
        self.isGameOver = True
        if self.current_player == 0:
            self.winner = 1
        else:
            self.winner = 0

    def get_board(self, board_num: int):
        self.check_input(board_num, NUMBER_OF_PLAYERS)
        return self.boards[board_num]
    
    def get_boards(self):
        return self.boards
    
    def get_dice(self):
        return self.dice
    
    def convert_value_to_emoji(self, value: int, special: bool=False) -> str:
        if value == 0:
            return "⬛"
        if special:
            match value:
                case 1:
                    return DICE_1_EMOJI
                case 2:
                    return DICE_2_EMOJI
                case 3:
                    return DICE_3_EMOJI
                case 4:
                    return DICE_4_EMOJI
                case 5:
                    return DICE_5_EMOJI
                case 6:
                    return DICE_6_EMOJI
        else:
            match value:
                case 1:
                    return "1️⃣"
                case 2:
                    return "2️⃣"
                case 3:
                    return "3️⃣"
                case 4:
                    return "4️⃣"
                case 5:
                    return "5️⃣"
                case 6:
                    return "6️⃣"
        if value < 0 or value > 6:
            raise ValueError("Value must be between 0 and 6, you provided: " + str(value))
    
    def get_embed(self) -> discord.Embed:
        game = "\n".join(f"`{self.calc_column_total(0, col):02d}` {self.convert_value_to_emoji(col+1) if self.current_player == 0 and not self.isGameOver else '🕯️'}{"".join(self.convert_value_to_emoji(_, True) for _ in self.boards[0][col][::-1])}{KNUKLEBONES_EMOJI}{"".join(self.convert_value_to_emoji(_, True) for _ in self.boards[1][col])}{self.convert_value_to_emoji(col+1) if self.current_player == 1 and not self.isGameOver else '🕯️'} `{self.calc_column_total(1, col):02d}`" for col in range(3))
        embed = discord.Embed(title=f"TURN {self.current_turn}", description=game, color=discord.Color.green() if self.isGameOver else discord.Color.blue() if self.current_player == 0 else discord.Color.yellow())
        
        embed.set_footer(text=f"Player 1: {self.calc_total(0):02d} | Player 2: {self.calc_total(1):02d} | Dice: {self.convert_value_to_emoji(self.dice)} | Game ID: {self.uuid}")

        if self.isGameOver:
            winner_text = "It's a tie!" if self.get_winner() == 2 else f"Player {self.get_winner() + 1} wins!"
            embed.add_field(name="Game Over", value=winner_text, inline=False)
        return embed
    
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
            "dice": self.dice,
            "winner": self.winner
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

    def save(self):
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