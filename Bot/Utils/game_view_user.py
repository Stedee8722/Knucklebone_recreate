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
    def __init__(self, game: game_util.KnuckleboneGame):
        super().__init__(timeout=None)
        self.game = game
        self.turn_deadline = round(datetime.now().timestamp() + 60)
        self.turn_timer_task = asyncio.create_task(self.turn_timer())
        self.latest_interaction = None

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
        await interaction.response.send_message(f"This game was closed due to an unexpected error. Please start a new game.", view=view)
        return await super().on_error(interaction, error, item)
    
    async def turn_timer(self):
        while not self.game.isGameOver:
            await asyncio.sleep(1)

            if self.turn_deadline and datetime.now().timestamp() > self.turn_deadline:
                self.game.resign()
                await self.check_disable()
                await self.time_expire()
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
    
    async def check_game_over(self, interaction) -> bool:
        if self.game.isGameOver:
            game_manager.remove_game(str(self.game.uuid))
            self.stop()
            await interaction.response.edit_message(content=f'Game over, gg!', embed=self.game.get_embed())
            return True
        self.turn_deadline = round(datetime.now().timestamp() + 60)
        return False

    async def time_expire(self) -> None:
        await self.latest_interaction.edit(content=f"Game ended because the turn timer expired, gg!", embed=self.game.get_embed())
        self.stop()
        game_manager.remove_game(str(self.game.uuid))
        return
    
    async def top(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.place_dice(0)
        await self.check_disable()
        if await self.check_game_over(interaction):
            return
        await interaction.response.edit_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        self.latest_interaction = await interaction.original_response()

    async def mid(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.place_dice(1)
        await self.check_disable()
        if await self.check_game_over(interaction):
            return
        await interaction.response.edit_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        self.latest_interaction = await interaction.original_response()

    async def bot(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.place_dice(2)
        await self.check_disable()
        if await self.check_game_over(interaction):
            return
        await interaction.response.edit_message(content=f"Hey **<@{self.game.players[self.game.current_player]}>**, it's your turn! Your die is: {self.game.convert_value_to_emoji(self.game.dice, True)}\n*Remaining time for move: <t:{self.turn_deadline}:R>*", embed=self.game.get_embed(), view=self)
        self.latest_interaction = await interaction.original_response()

    async def resign(self, interaction:discord.Interaction) -> None:
        if not await self.check_owner(interaction): return
        self.game.resign()
        await self.check_disable()
        if await self.check_game_over(interaction):
            return
        await interaction.response.edit_message(content="", embed=self.game.get_embed(), view=self)
        self.latest_interaction = await interaction.original_response()