import discord, main, asyncio, random, datetime
from Utils import game_util, error_view
from datetime import datetime
from Utils import game_manager

class CallbackButton(discord.ui.Button):
    def __init__(self, label, callback, cid=None, disabled=False, emoji=None, style=discord.ButtonStyle.blurple):
        super().__init__(style=style, label=label, custom_id=cid, disabled=disabled, emoji=emoji)
        self.to_callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self.to_callback(interaction)

class GameView(discord.ui.View):
    def __init__(self, game: game_util.KnuckleboneGame, edit_game_message, log_moves, delete_thread_after_game, channel, thread = None):
        super().__init__(timeout=None)
        self.game = game
        self.edit_game_message = edit_game_message
        self.log_moves = log_moves
        self.delete_thread_after_game = delete_thread_after_game
        self.thread = thread
        self.turn_deadline = round(datetime.now().timestamp() + 120)
        self.channel = channel
        self.turn_timer_task = asyncio.create_task(self.turn_timer())

        self.top_button = CallbackButton(label="Top", callback=self.top, cid="top", emoji="1️⃣", disabled=False if self.game.check_column_space(0) else True)
        self.mid_button = CallbackButton(label="Mid", callback=self.mid, cid="mid", emoji="2️⃣", disabled=False if self.game.check_column_space(1) else True)
        self.bot_button = CallbackButton(label="Bot", callback=self.bot, cid="bot", emoji="3️⃣", disabled=False if self.game.check_column_space(2) else True)
        self.resign_button = CallbackButton(label="Resign", callback=self.resign, cid="resign", emoji="🏳️", style=discord.ButtonStyle.red)
        self.add_item(self.top_button)
        self.add_item(self.mid_button)
        self.add_item(self.bot_button)
        self.add_item(self.resign_button)

    async def on_error(self, interaction: discord.Interaction[discord.Client], error: Exception, item) -> None:
        main.logger.error(f"Error in GameView: {error}, item: {item}, interaction: {interaction}")
        view = error_view.ErrorView("This game was closed due to an unexpected error. Please start a new game.", f"Debug info: {error} | {item} | {interaction}")
        await interaction.channel.send(f"This game was closed due to an unexpected error. Please start a new game.", view=view)
        return await super().on_error(interaction, error, item)
    
    async def turn_timer(self):
        while not self.game.isGameOver:
            await asyncio.sleep(1)

            if self.turn_deadline and datetime.now().timestamp() > self.turn_deadline:
                self.game.resign()
                await self.check_disable()
                await self.channel.send(f"Game ended because the turn timer expired.", embed=self.game.get_embed())
                await self.check_game_over(self.thread)
                break

    async def check_disable(self):
        self.top_button.disabled = not self.game.check_column_space(0) or self.game.isGameOver or (self.game.bot_player and self.game.current_player == 1)
        self.mid_button.disabled = not self.game.check_column_space(1) or self.game.isGameOver or (self.game.bot_player and self.game.current_player == 1)
        self.bot_button.disabled = not self.game.check_column_space(2) or self.game.isGameOver or (self.game.bot_player and self.game.current_player == 1)
        self.resign_button.disabled = self.game.isGameOver

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.game.players[self.game.current_player]:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return False
        return True
    
    async def check_game_over(self, channel) -> bool:
        if self.game.isGameOver:
            game_manager.remove_game(str(self.game.uuid))
            asyncio.create_task(self.game_over(channel)) 
            return True
        self.turn_deadline = round(datetime.now().timestamp() + 120)
        return False

    async def game_over(self, channel) -> None:
        self.stop()
        if self.delete_thread_after_game and self.thread:
            await self.thread.send(f'Game will self-destruct <t:{datetime.now().timestamp().__round__() + 60}:R>. Say "gg" while you can!')
            await asyncio.sleep(60)
            try:
                await self.thread.delete()
            except discord.errors.NotFound:
                pass 
        else:
            await channel.send(f'Game over, gg!')
    
    async def top(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.place_dice(0)
        await self.check_disable()
        if self.log_moves:
            await interaction.channel.send(f"**{self.game.player_one.name if self.game.current_player == 1 else self.game.player_two.name}** places {self.game.convert_value_to_emoji(self.game.last_dice, True)} in 1️⃣ **Top**!", allowed_mentions=False)
        if self.edit_game_message:
            await interaction.response.edit_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        else:
            await interaction.response.send_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        if await self.check_game_over(interaction.channel):
            return
        if self.game.bot_player:
            await self.simulate_bot_move(interaction)

    async def mid(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.place_dice(1)
        await self.check_disable()
        if self.log_moves:
            await interaction.channel.send(f"**{self.game.player_one.name if self.game.current_player == 1 else self.game.player_two.name}** places {self.game.convert_value_to_emoji(self.game.last_dice, True)} in 2️⃣ **Mid**!", allowed_mentions=False)
        if self.edit_game_message:
            await interaction.response.edit_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        else:
            await interaction.response.send_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        if await self.check_game_over(interaction.channel):
            return
        if self.game.bot_player:
            await self.simulate_bot_move(interaction)

    async def bot(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.place_dice(2)
        await self.check_disable()
        if self.log_moves:
            await interaction.channel.send(f"**{self.game.player_one.name if self.game.current_player == 1 else self.game.player_two.name}** places {self.game.convert_value_to_emoji(self.game.last_dice, True)} in 3️⃣ **Bot**!", allowed_mentions=False)
        if self.edit_game_message:
            await interaction.response.edit_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        else:
            await interaction.response.send_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        if await self.check_game_over(interaction.channel):
            return
        if self.game.bot_player:
            await self.simulate_bot_move(interaction)

    async def resign(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.resign()
        await self.check_disable()
        if self.edit_game_message:
            await interaction.response.edit_message(content="", embed=self.game.get_embed(), view=self)
        else:
            await interaction.response.send_message(content="", embed=self.game.get_embed(), view=self)
        if await self.check_game_over(interaction.channel):
            return

    async def start_bot_move(self, interaction:discord.Interaction) -> None:
        if self.game.bot_player and not self.game.isGameOver and self.game.current_player == 1:
            await asyncio.sleep(random.randint(1, 3) * random.random()) # Simulate thinking time
            last_move = self.game.AI_move(self.game.random_stupidity)
            self.game.place_dice(last_move)
            await self.check_disable()
            if self.log_moves:
                await interaction.channel.send(f"**{self.game.player_one.name if self.game.current_player == 1 else self.game.player_two.name}** places {self.game.convert_value_to_emoji(self.game.last_dice, True)} in {['1️⃣ **Top**', '2️⃣ **Mid**', '3️⃣ **Bot**'][last_move]}!", allowed_mentions=False)
            if self.edit_game_message:
                await interaction.edit(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
            else:
                await interaction.channel.send(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
            if await self.check_game_over(interaction.channel):
                return

    async def simulate_bot_move(self, interaction:discord.Interaction) -> None:
        if self.game.bot_player and not self.game.isGameOver and self.game.current_player == 1:
            await asyncio.sleep(random.randint(1, 3) * random.random()) # Simulate thinking time
            last_move = self.game.AI_move(self.game.random_stupidity)
            self.game.place_dice(last_move)
            await self.check_disable()
            if self.log_moves:
                await interaction.channel.send(f"**{self.game.player_one.name if self.game.current_player == 1 else self.game.player_two.name}** places {self.game.convert_value_to_emoji(self.game.last_dice, True)} in {['1️⃣ **Top**', '2️⃣ **Mid**', '3️⃣ **Bot**'][last_move]}!", allowed_mentions=False)
            if self.edit_game_message:
                await interaction.message.edit(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
            else:
                await interaction.channel.send(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
            if await self.check_game_over(interaction.channel):
                return