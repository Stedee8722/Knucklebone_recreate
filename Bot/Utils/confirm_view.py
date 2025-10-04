import discord, main, json
from Utils import game_util, game_view, game_manager

class ConfirmView(discord.ui.View):
    def __init__(self, player_one, player_two, id_of_opponent, game_number, games_in_thread, edit_game_message, log_moves, delete_thread_after_game, thread = None, game = None):
        super().__init__(timeout=180)
        self.player_one = player_one
        self.player_two = player_two
        self.id_of_opponent = id_of_opponent
        self.game_number = game_number
        self.games_in_thread = games_in_thread
        self.edit_game_message = edit_game_message
        self.log_moves = log_moves
        self.delete_thread_after_game = delete_thread_after_game
        self.thread = thread
        self.message = None
        self.game = game

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.id_of_opponent:
            await interaction.response.send_message("This isn't for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="confirm_yes")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_owner(interaction): return
        if not self.game:
            flag = 1
            game = game_util.KnuckleboneGame(self.player_one, self.player_two, self.game_number, interaction.guild.id)
            game.start_game()
            view = game_view.GameView(game, self.edit_game_message, self.log_moves, self.delete_thread_after_game, self.thread)
        else:
            flag = 0
            game = self.game
            view = game_view.GameView(game, self.edit_game_message, self.log_moves, self.delete_thread_after_game, self.thread)
        self.stop()
        
        await interaction.response.edit_message(content=f"**{self.player_two.name}** accepted a Knucklebones challenge from **{self.player_one.name}**.", view=None)
        if self.games_in_thread:
            try:
                thread = await interaction.channel.create_thread(name = f"Game {self.game_number} - {self.player_one.name} & {self.player_two.name}{" (Reload)" if not flag else ""}", type = discord.ChannelType.public_thread)
                view.thread = thread
                await thread.add_user(self.player_one)
                await thread.add_user(self.player_two)
                await thread.send(content=f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())
            except AttributeError:
                await interaction.channel.send("Error: Can't create threads here.")
                return
            if flag:
                with open("Data/server_config.json", "r") as file:
                    server_config = json.load(file)
                if server_config[f"{interaction.guild.id}"]["game_counter"] >= game.game_number:
                    server_config[f"{interaction.guild.id}"]["game_counter"] += 1
                    with open("Data/bot_data.json", "w") as file:
                        json.dump(server_config, file, indent=4)
            game_manager.add_game(str(game.uuid))
        else:
            await interaction.channel.send(f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())

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
        await interaction.channel.send(f"An error occurred while handling your request. Please try again.\n-# Debug info: {error} | {item} | {interaction}")
        return await super().on_error(interaction, error, item)