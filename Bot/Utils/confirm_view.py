import discord, main
from Utils import game_util, game_view

class CallbackButton(discord.ui.Button):
    def __init__(self, label, callback, cid=None, disabled=False, emoji=None, style=discord.ButtonStyle.blurple):
        super().__init__(style=style, label=label, custom_id=cid, disabled=disabled, emoji=emoji)
        self.to_callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self.to_callback(interaction)

class ConfirmView(discord.ui.View):
    def __init__(self, player_one, player_two):
        super().__init__(timeout=120)
        self.player_one = player_one
        self.player_two = player_two
        self.message = None       

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.player_two.id:
            await interaction.response.send_message("This isn't for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm_yes", emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction): return
        
        game = game_util.KnuckleboneGame(self.player_one, self.player_two)
        game.start_game()
        view = game_view.GameView(game)

        self.stop()
        await interaction.response.edit_message(content=f"**{self.player_two.name}** accepted a Knucklebones challenge from **{self.player_one.name}**.", view=None)
        await interaction.channel.send(f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="confirm_no", emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction): return

        self.stop()
        await interaction.response.edit_message(content=f"**{self.player_two.name}** declined a Knucklebones challenge from **{self.player_one.name}**.", view=None)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        
        self.stop()
        await self.message.edit(content=f"**{self.player_two.name}** declined a Knucklebones challenge from **{self.player_one.name}**.", view=None)

    async def on_error(self, interaction: discord.Interaction[discord.Client], error: Exception, item) -> None:
        main.logger.error(f"Error in ConfirmView: {error}, item: {item}, interaction: {interaction}")
        await interaction.response.send_message(f"An error occurred while handling your request. Please try again.\n-# Debug info: {error} | {item} | {interaction}", ephemeral=True)
        return await super().on_error(interaction, error, item)