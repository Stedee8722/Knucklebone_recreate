import discord, main, json
from Utils import game_util, game_view_user, game_manager, error_view
from Exceptions.BotError import GameInitError

class ConfirmView(discord.ui.View):
    def __init__(self, player_one, player_two, id_of_opponent, game_number):
        super().__init__(timeout=180)
        self.player_one = player_one
        self.player_two = player_two
        self.id_of_opponent = id_of_opponent
        self.game_number = game_number
        self.message = None

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.id_of_opponent:
            await interaction.response.send_message("This isn't for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="confirm_yes")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction): return
        game = game_util.KnuckleboneGame(player_one=self.player_one, player_two=self.player_two, game_number=self.game_number, guild_id=interaction.guild.id, bot_player=False, user_mode=True)
        game.start_game()
        view = game_view_user.GameView(game)
        self.stop()
        
        with open("Data/server_data.json", "r") as file:
            server_data = json.load(file)
        if server_data[f"{interaction.guild.id}"]["game_counter"] >= game.game_number:
            server_data[f"{interaction.guild.id}"]["game_counter"] += 1
            with open("Data/server_data.json", "w") as file:
                json.dump(server_data, file, indent=4)

        await interaction.response.send_message(f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}\n*Remaining time for move: <t:{view.turn_deadline}:R>*", view=view, embed=game.get_embed())
        view.latest_interaction = await interaction.original_response()
        game_manager.add_game(str(game.uuid))

    @discord.ui.button(label="No", style=discord.ButtonStyle.grey, custom_id="confirm_no")
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
        view = error_view.ErrorView("An error occurred while handling your request. Please try again.", f"Debug info: {error} | {item} | {interaction}")
        await interaction.response.send_message(f"An error occurred while handling your request. Please try again.", view=view)
        return await super().on_error(interaction, error, item)