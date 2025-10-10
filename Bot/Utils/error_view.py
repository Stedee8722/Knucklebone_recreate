import discord

class ErrorView(discord.ui.View):
    def __init__(self, message: str, debug_info: str = None):
        super().__init__(timeout=None)
        self.message = message
        self.debug_info = debug_info

    @discord.ui.button(label="Debug Info", style=discord.ButtonStyle.secondary, custom_id="debug_info")
    async def debug_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content=f"{self.message}\n-# {self.debug_info}", view=None)