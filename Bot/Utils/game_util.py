import random, uuid, discord, main

NUMBER_OF_PLAYERS = 2
NUMBER_OF_COLUMNS = 3
NUMBER_OF_DICES_PER_COLUMN = 3
NUMBER_OF_SIDES_PER_DICE = 6
SAVE_FILE = "Data/game_data.json"
USER_DATA_FILE = "Data/user_data.json"
BOT_DATA_FILE = "Data/bot_data.json"
SERVER_DATA_FILE = "Data/server_data.json"
KNUKLEBONES_EMOJI = "<:knucklebones:1423761306447511552>"
DICE_1_EMOJI = "<:dice_1:1423761282183594246>"
DICE_2_EMOJI = "<:dice_2:1423761286747131904>"
DICE_3_EMOJI = "<:dice_3:1423761292677873724>"
DICE_4_EMOJI = "<:dice_4:1423761295001522198>"
DICE_5_EMOJI = "<:dice_5:1423761297568174101>"
DICE_6_EMOJI = "<:dice_6:1423761301423001630>"

class KnuckleboneGame:
    def __init__(self, player_one: discord.Member, player_two: discord.Member, game_number:int, guild_id:int, bot_player: bool = False):
        self.boards = [
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],  # Player 1's board
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]]   # Player 2's board
        ]
        self.isGameOver = False
        self.game_number = game_number
        self.current_player = -1  # Random player starts
        self.uuid = uuid.uuid4()
        self.guild_id = guild_id
        self.player_one = player_one
        self.player_two = player_two
        self.players = [player_one.id, player_two.id]
        self.dice = 0
        self.current_turn = 0
        self.turn_history = []  # To keep track of turns
        self.winner = -1  # -1 means no winner yet
        self.last_dice = 0
        self.bot_player = bot_player
        if bot_player:
            self.random_stupidity = random.randint(1, 10)
        else:
            self.random_stupidity = 0

    def start_game(self) -> None:
        self.current_player = random.randint(0, 1)
        self.current_turn = 1
        self.roll_dice()

    def next_turn(self) -> None:
        self.current_player = 1 - self.current_player
        self.current_turn += 1
        self.roll_dice()
    
    def roll_dice(self) -> int:
        self.last_dice = self.dice
        self.dice = random.randint(1, 6)
        self.save()
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
        if not self.isGameOver:
            self.next_turn()

    def AI_move(self, random_stupidity: float) -> int:
        if random.random() > random_stupidity:
            available = [i for i in range(NUMBER_OF_COLUMNS) if self.check_column_space(i)]
            result = random.choice(available)
            print("Be stupid")
            return result
        scores = [0] * NUMBER_OF_COLUMNS
        for i, column in enumerate(self.boards[1 - self.current_player]):
            if not self.check_column_space(i):
                scores[i] = -1
                continue
            else:
                match self.count_matching_dice_opponent(i):
                    case 0:
                        scores[i] += 0
                    case 1:
                        scores[i] += 1
                    case 2:
                        scores[i] += 2
                    case 3:
                        scores[i] += 5
                match self.count_matching_dice_self(i):
                    case 0:
                        scores[i] += 0
                    case 1:
                        scores[i] += 1
                    case 2:
                        scores[i] += 2
                    case 3:
                        scores[i] += 5
        best_score = max(scores)
        best_columns = [i for i, score in enumerate(scores) if score == best_score]
        return random.choice(best_columns)

    def save_turn_history(self, column: int) -> None:
        self.turn_history.append({"board": self.current_player, "column": column, "dice": self.dice, "turn": self.current_turn})

    def count_matching_dice_self(self, column: int) -> int:
        count = 0
        for die in self.boards[self.current_player][column]:
            if die == self.dice:
                count += 1
        return count

    def count_matching_dice_opponent(self, column: int) -> int:
        count = 0
        for die in self.boards[1 - self.current_player][column]:
            if die == self.dice:
                count += 1
        return count

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

    def check_game_over(self) -> None:
        board = self.boards[self.current_player]
        for column in board:
            if 0 in column:
                return False
        self.isGameOver = True
        self.current_turn += 1
        self.current_player = 1 - self.current_player
        self.last_dice = self.dice
        self.get_winner()
        self.save()
        self.save_data()
        return
    
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
        self.save()
        self.save_data()

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
    
    # ---------------- EMBED ----------------

    def get_embed(self) -> discord.Embed:
        game = "\n".join(f"`{self.calc_column_total(0, col):02d}` {self.convert_value_to_emoji(col+1) if self.current_player == 0 and not self.isGameOver else '🕯️'}{"".join(self.convert_value_to_emoji(_, True) for _ in self.boards[0][col][::-1])}{KNUKLEBONES_EMOJI}{"".join(self.convert_value_to_emoji(_, True) for _ in self.boards[1][col])}{self.convert_value_to_emoji(col+1) if self.current_player == 1 and not self.isGameOver else '🕯️'} `{self.calc_column_total(1, col):02d}`" for col in range(3))
        embed = discord.Embed(title=f"TURN {self.current_turn}{f" -- {[f"{self.player_one.name} wins!", f"{self.player_two.name} wins!", "Ties"][self.get_winner()]}" if self.get_winner() >= 0 else ""}", description=game, color=discord.Color.green() if self.isGameOver else discord.Color.blue() if self.current_player == 0 else discord.Color.yellow())
        
        embed.add_field(name = self.player_one.name, value=self.calc_total(0), inline=True)
        embed.add_field(name = self.player_two.name, value=self.calc_total(1), inline=True)

        embed.set_footer(text=f"Game ID: {self.uuid}")

        #if self.isGameOver:
        #    winner_text = "It's a tie!" if self.get_winner() == 2 else f"Player {self.get_winner() + 1} wins!"
        #    embed.add_field(name="Game Over", value=winner_text, inline=False)
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
            "players": self.players,
            "turn_history": self.turn_history,
            "dice": self.dice,
            "winner": self.winner,
            "current_turn": self.current_turn,
            "bot_player": self.bot_player,
            "random_stupidity": self.random_stupidity,
            "game_number": self.game_number
        }

    @classmethod
    def from_dict(cls, ctx, data: dict):
        game = cls(ctx.guild.get_member(data["players"][0]), ctx.guild.get_member(data["players"][1]), data["game_number"], data["bot_player"])
        game.uuid = uuid.UUID(data["uuid"])
        game.boards = data["boards"]
        game.isGameOver = data["isGameOver"]
        game.current_player = data["current_player"]
        game.turn_history = data["turn_history"]
        game.dice = data["dice"]
        game.current_turn = data["current_turn"]
        game.random_stupidity = data["random_stupidity"]
        return game

    def save(self):
        """Save the current game state to a file."""
        import json, os
        if not os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "w") as f:
                json.dump({}, f)

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        if f"{self.guild_id}" not in data:
            data[f"{self.guild_id}"] = {}

        data[f"{self.guild_id}"][str(self.uuid)] = self.to_dict()

        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load(ctx, game_id: str):
        """Load game by id from the save file."""
        import json, os
        if not os.path.exists(SAVE_FILE):
            return None

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        if game_id not in data:
            return None

        return KnuckleboneGame.from_dict(ctx, data[ctx.guild.id][game_id])
    
    def save_data(self):
        import json, os
        if not os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "w") as f:
                json.dump({}, f)
        if not os.path.exists(BOT_DATA_FILE):
            with open(BOT_DATA_FILE, "w") as f:
                json.dump({}, f)
        if not os.path.exists(SERVER_DATA_FILE):
            with open(SERVER_DATA_FILE, "w") as f:
                json.dump({}, f)
        

        with open(USER_DATA_FILE, "r") as f:
            user_data = json.load(f)
        with open(BOT_DATA_FILE, "r") as f:
            bot_data = json.load(f)
        with open(SERVER_DATA_FILE, "r") as f:
            server_data = json.load(f)

        
        if str(self.players[0]) not in user_data:
            user_data[str(self.players[0])] = {
                "used_commands": 0,
                "kb_wins": 0,
                "kb_losses": 0,
                "kb_games_played": 0
            }
        if str(self.players[1]) not in user_data:
            user_data[str(self.players[1])] = {
                "used_commands": 0,
                "kb_wins": 0,
                "kb_losses": 0,
                "kb_games_played": 0
            }
        if str(self.players[0]) not in server_data[f"{self.guild_id}"]["users"]:
            server_data[f"{self.guild_id}"]["users"][str(self.players[0])] = {
                "used_commands": 0,
                "kb_wins": 0,
                "kb_losses": 0,
                "kb_games_played": 0
            }
        if str(self.players[1]) not in server_data[f"{self.guild_id}"]["users"]:
            server_data[f"{self.guild_id}"]["users"][str(self.players[1])] = {
                "used_commands": 0,
                "kb_wins": 0,
                "kb_losses": 0,
                "kb_games_played": 0
            }
        if self.players[0] != self.players[1]:
            if self.winner == 0:
                user_data[str(self.players[0])]["kb_wins"] += 1
                user_data[str(self.players[1])]["kb_losses"] += 1
                server_data[f"{self.guild_id}"]["users"][str(self.players[0])]["kb_wins"] += 1
                server_data[f"{self.guild_id}"]["users"][str(self.players[1])]["kb_losses"] += 1
            elif self.winner == 1:
                user_data[str(self.players[1])]["kb_wins"] += 1
                user_data[str(self.players[0])]["kb_losses"] += 1
                server_data[f"{self.guild_id}"]["users"][str(self.players[1])]["kb_wins"] += 1
                server_data[f"{self.guild_id}"]["users"][str(self.players[0])]["kb_losses"] += 1
        user_data[str(self.players[0])]["kb_games_played"] += 1
        server_data[f"{self.guild_id}"]["users"][str(self.players[0])]["kb_games_played"] += 1
        if self.players[0] != self.players[1]:
            user_data[str(self.players[1])]["kb_games_played"] += 1
            server_data[f"{self.guild_id}"]["users"][str(self.players[1])]["kb_games_played"] += 1

        if "total_games_played" not in bot_data:
            bot_data["total_games_played"] = 0
        bot_data["total_games_played"] += 1

        if "total_games_played" not in server_data[f"{self.guild_id}"]:
            server_data[f"{self.guild_id}"]["total_games_played"] = 0
        server_data[f"{self.guild_id}"]["total_games_played"] += 1

        with open(BOT_DATA_FILE, "w") as f:
            json.dump(bot_data, f, indent=4)
        with open(USER_DATA_FILE, "w") as f:
            json.dump(user_data, f, indent=4)
        with open(SERVER_DATA_FILE, "w") as f:
            json.dump(server_data, f, indent=4)