import discord, main, json
from Utils import embed_util

def check_index(index: int) -> int:
    """Check if the index is within the bounds of the dice data.
    Args:  
        index (int): The index to check.
    Returns:
        int: The adjusted index, ensuring it is within the valid range.
    Raises:
        None
    1. If index is less than 0, return the last index.
    2. If index is greater than the last index, return 0.
    3. If index is valid, return the index as is.
    """
    with open("Data/user_data.json", "r") as file:
        user_data = json.load(file)
    data_length = len(list(user_data.keys()))
    if index < 0:
        return data_length - 1
    elif index > data_length - 1:
        return 0
    else:
        return index

class CallbackButton(discord.ui.Button):
    def __init__(self, label, callback, cid=None, disabled=False, emoji=None, style=discord.ButtonStyle.blurple):
        super().__init__(style=style, label=label, custom_id=cid, disabled=disabled, emoji=emoji)
        self.to_callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self.to_callback(interaction)

class setting_option(discord.ui.View):
    def __init__(self, bot: discord.Client, ctx, page):
        super().__init__(timeout=180)
        self.bot = bot
        self.ctx = ctx
        self.index = page
        self.ended = False
        self.add_item(CallbackButton(label="Back",style=discord.ButtonStyle.primary, cid="back", emoji="◀️", callback=self.back))
        self.add_item(CallbackButton(label="Bot Info",style=discord.ButtonStyle.secondary, cid="bot_info", emoji="🤖", callback=self.bot_info))
        self.add_item(CallbackButton(label="Next",style=discord.ButtonStyle.primary, cid="next", emoji="▶️", callback=self.next))
        
    async def on_timeout(self) -> None:
        return await super().on_timeout()

    async def on_error(self, interaction: discord.Interaction[discord.Client], error: Exception, item) -> None:
        main.logger.error(error)
        return await super().on_error(interaction, error, item)
    
    async def back(self,interaction:discord.Interaction):
        # Check if the interaction user is the same as the command author
        if self.ctx.author != interaction.user:
            await interaction.response.send_message("This button isn't for you", ephemeral=True)
        else:
            self.index = check_index(self.index-1)
            with open("Data/user_data.json", "r") as file:
                user_data = json.load(file)
            with open("Data/bot_data.json", "r") as file:
                bot_data = json.load(file)
            id = list(user_data.keys())[self.index]
            await interaction.response.edit_message(content="", embed = await embed_util.random_stats_embed_build(self.ctx, 1, user_data[id], bot_data["last_reset"], id))

    async def bot_info(self,interaction:discord.Interaction):
        # Check if the interaction user is the same as the command author
        if self.ctx.author != interaction.user:
            await interaction.response.send_message("This button isn't for you", ephemeral=True)
        else:
            self.index = -1
            with open("Data/bot_data.json", "r") as file:
                bot_data = json.load(file)
            await interaction.response.edit_message(content="", embed = await embed_util.random_stats_embed_build(self.ctx, 0, bot_data, bot_data["last_reset"]))

    async def next(self,interaction:discord.Interaction):
        # Check if the interaction user is the same as the command author
        if self.ctx.author != interaction.user:
            await interaction.response.send_message("This button isn't for you", ephemeral=True)
        else:
            self.index = check_index(self.index+1)
            with open("Data/user_data.json", "r") as file:
                user_data = json.load(file)
            with open("Data/bot_data.json", "r") as file:
                bot_data = json.load(file)
            id = list(user_data.keys())[self.index]
            await interaction.response.edit_message(content="", embed = await embed_util.random_stats_embed_build(self.ctx, 1, user_data[id], bot_data["last_reset"], id))