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
        self.add_item(CallbackButton(label="Top", callback=self.top, cid="top", emoji="1️⃣"))
        self.add_item(CallbackButton(label="Mid", callback=self.mid, cid="mid", emoji="2️⃣"))
        self.add_item(CallbackButton(label="Bot", callback=self.bot, cid="bot", emoji="3️⃣"))
        self.add_item(CallbackButton(label="Resign", callback=self.resign, cid="resign", emoji="🏳️", style=discord.ButtonStyle.red))

    async def on_error(self, interaction: discord.Interaction[discord.Client], error: Exception, item) -> None:
        main.logger.error(error)
        return await super().on_error(interaction, error, item)
    
    async def top(self, interaction:discord.Interaction) -> None:
        print("top")
        pass

    async def mid(self, interaction:discord.Interaction) -> None:
        print("mid")
        pass

    async def bot(self, interaction:discord.Interaction) -> None:
        print("bot")
        pass

    async def resign(self, interaction:discord.Interaction) -> None:
        print("resign")
        pass