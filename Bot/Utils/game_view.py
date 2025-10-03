import discord, main
from Utils import game_util

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
        self.top_button = CallbackButton(label="Top", callback=self.top, cid="top", emoji="1️⃣", disabled=False if self.game.check_column_space(0) else True)
        self.mid_button = CallbackButton(label="Mid", callback=self.mid, cid="mid", emoji="2️⃣", disabled=False if self.game.check_column_space(1) else True)
        self.bot_button = CallbackButton(label="Bot", callback=self.bot, cid="bot", emoji="3️⃣", disabled=False if self.game.check_column_space(2) else True)
        self.resign_button = CallbackButton(label="Resign", callback=self.resign, cid="resign", emoji="🏳️", style=discord.ButtonStyle.red)
        self.add_item(self.top_button)
        self.add_item(self.mid_button)
        self.add_item(self.bot_button)
        self.add_item(self.resign_button)

    async def check_disable(self):
        self.top_button.disabled = not self.game.check_column_space(0) or self.game.isGameOver
        self.mid_button.disabled = not self.game.check_column_space(1) or self.game.isGameOver
        self.bot_button.disabled = not self.game.check_column_space(2) or self.game.isGameOver
        self.resign_button.disabled = self.game.isGameOver
        await self.check_stop()

    async def check_stop(self) -> None:
        if self.game.isGameOver:
            self.stop()

    async def on_error(self, interaction: discord.Interaction[discord.Client], error: Exception, item) -> None:
        main.logger.error(error)
        return await super().on_error(interaction, error, item)
    
    async def top(self, interaction:discord.Interaction) -> None:
        print("top")
        self.game.place_dice(0)
        await self.check_disable()
        await interaction.response.edit_message(embed=self.game.get_embed(), view=self)

    async def mid(self, interaction:discord.Interaction) -> None:
        print("mid")
        self.game.place_dice(1)
        await self.check_disable()
        await interaction.response.edit_message(embed=self.game.get_embed(), view=self)

    async def bot(self, interaction:discord.Interaction) -> None:
        print("bot")
        self.game.place_dice(2)
        await self.check_disable()
        await interaction.response.edit_message(embed=self.game.get_embed(), view=self)

    async def resign(self, interaction:discord.Interaction) -> None:
        print("resign")
        self.game.resign()
        await self.check_disable()
        await interaction.response.edit_message(embed=self.game.get_embed(), view=self)