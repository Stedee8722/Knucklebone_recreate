from typing import List
import discord, time, datetime, json
from discord.ext import commands
from discord import app_commands
from Utils import game_view, game_util, confirm_view, game_manager

class KnucklebonesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="knucklebones", description="Play a game of Knucklebones!", with_app_command=True)
    @app_commands.describe(opponent="Your opponent?", uuid="(Optional) The UUID of the game you want to load.")
    async def knucklebones(self, ctx: commands.Context, opponent: discord.Member, uuid: str = None):
        try:
            with open("Data/server_config.json", "r") as file:
                server_config = json.load(file)
            games_in_thread = server_config[f"{ctx.guild.id}"]["games_in_thread"]
            specified_channel = server_config[f"{ctx.guild.id}"]["specified_channel"]
            channel_to_send = ctx.guild.get_channel(int(specified_channel)) if specified_channel else ctx.channel
            edit_game_message = server_config[f"{ctx.guild.id}"]["edit_game_message"]
            log_moves = server_config[f"{ctx.guild.id}"]["log_moves"]
            delete_thread_after_game = server_config[f"{ctx.guild.id}"]["delete_thread_after_game"]
            await ctx.defer(ephemeral=False)
            if uuid:
                if game_manager.is_active(uuid):
                    await ctx.reply("This game is already running in another thread or channel!")
                    return
                game = game_util.KnuckleboneGame.load(ctx, uuid)
                if not game:
                    await ctx.reply("Can't find game!")
                    return
                if not ctx.author.id in game.players:
                    await ctx.reply("This is not your game!")
                    return
                if game.isGameOver:
                    await ctx.reply("Game is already over!")
                    return
                if opponent.id not in game.players:
                    await ctx.reply("Wrong opponent!")
                    return
                if game.player_two.id == ctx.bot.user.id or game.player_one.id == game.player_two.id == ctx.author.id:
                    await ctx.reply("So! We continue.")
                    if games_in_thread:
                        thread = await channel_to_send.create_thread(name = f"Game {game.game_number} - {game.player_one.name} & {game.player_two.name} (Reload)", type = discord.ChannelType.public_thread)
                        view = game_view.GameView(game, edit_game_message, log_moves, delete_thread_after_game, thread)
                        await thread.add_user(ctx.author)
                        await thread.send(content=f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())
                    else:
                        view = game_view.GameView(game, edit_game_message, log_moves, delete_thread_after_game)
                        await channel_to_send.send(content=f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())
                    game_manager.add_game(uuid)
                    return
                view = confirm_view.ConfirmView(game.player_one, game.player_two, opponent.id, game.game_number, games_in_thread, edit_game_message, log_moves, delete_thread_after_game, game = game)
                await ctx.send(f"You have challenged **{opponent.name}** to continue a game of knucklebones!")
                await channel_to_send.send(content=f"<@{opponent.id}>! You have been challenged to continue a game of Knucklebones by **{ctx.author.name}**. Do you accept?\nThis challenge will expire in <t:{datetime.datetime.now().timestamp().__round__() + 180}:R>.", view=view, embed=game.get_embed())
                return
            with open("Data/server_data.json", "r") as file:
                server_data = json.load(file)
            game_number = server_data[f"{ctx.guild.id}"]["game_counter"]
            if opponent.id == ctx.bot.user.id:
                game = game_util.KnuckleboneGame(ctx.author, ctx.bot.user, game_number, ctx.guild.id, True)
                game.start_game()
                message = await ctx.reply("Oh, you're challenging me?")
                time.sleep(2)
                if games_in_thread:
                    # specified channel
                    thread = await channel_to_send.create_thread(name = f"Game {game_number} - {ctx.author.name} & {opponent.name}", type = discord.ChannelType.public_thread)
                    view = game_view.GameView(game, edit_game_message, log_moves, delete_thread_after_game, thread)
                    await thread.add_user(ctx.author)
                    message = await thread.send(content=f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())
                else:
                    view = game_view.GameView(game, edit_game_message, log_moves, delete_thread_after_game)
                    await channel_to_send.send(content=f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())
                with open("Data/server_data.json", "r") as file:
                    server_data = json.load(file)
                if server_data[f"{ctx.guild.id}"]["game_counter"] >= game.game_number:
                    server_data[f"{ctx.guild.id}"]["game_counter"] += 1
                    with open("Data/server_data.json", "w") as file:
                        json.dump(server_data, file, indent=4)
                game_manager.add_game(str(game.uuid))
                if game.current_player == 1:
                    await view.start_bot_move(message)
                return
            if opponent.bot:
                return await ctx.reply("You cannot play against other bots, please against me instead!")
            view = confirm_view.ConfirmView(ctx.author, opponent, opponent.id, game_number, games_in_thread, edit_game_message, log_moves, delete_thread_after_game)
            await ctx.send(f"You have challenged **{opponent.name}** to a game of knucklebones!")
            # specified channel
            message = await channel_to_send.send(f"<@{opponent.id}>! You have been challenged to a game of Knucklebones by **{ctx.author.name}**. Do you accept?\nThis challenge will expire in <t:{datetime.datetime.now().timestamp().__round__() + 180}:R>.", view=view)
            view.message = message
        except AttributeError:
            await channel_to_send.send("Error: Can't create threads here.")
            return
        
    @commands.hybrid_command(name="set-channel", with_app_command=True, description="Sets channel to play Knucklebones")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(channel="The channel to make games")
    async def set_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        with open("Data/server_config.json", "r") as file:
            server_config = json.load(file)
        if not channel:
            server_config[f"{ctx.guild.id}"]["specified_channel"] = 0
            with open("Data/server_config.json", "w") as file:
                json.dump(server_config, file, indent=4)
            await ctx.reply(f"Set channel to None", ephemeral=True)
            return
        server_config[f"{ctx.guild.id}"]["specified_channel"] = channel.id
        with open("Data/server_config.json", "w") as file:
            json.dump(server_config, file, indent=4)
        await ctx.reply(f"Set channel to {channel.name} ({channel.id})", ephemeral=True)

    @commands.hybrid_command(name="configure", with_app_command=True, description="Set the bot's config for your server", aliases=["config"])
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(config="The config")
    async def configure(self, ctx: commands.Context, config:str, value:int=-1):
        default_config = {
            "games_in_thread": 1,
            "specified_channel": 0,
            "edit_game_message": 0,
            "log_moves": 1,
            "delete_thread_after_game": 1
        }
        with open("Data/server_config.json", "r") as file:
            server_config = json.load(file)
        if f"{ctx.guild.id}" not in server_config:
            server_config[f"{ctx.guild.id}"] = default_config
        if config == "reset_all":
            server_config[f"{ctx.guild.id}"] = default_config
            with open("Data/server_config.json", "w") as file:
                json.dump(server_config, file, indent=4)
            await ctx.reply(f"Set all config to default values", ephemeral=True)
            return
        elif value == -1:
            server_config[f"{ctx.guild.id}"][config] = 1 - server_config[f"{ctx.guild.id}"][config]
        else:
            server_config[f"{ctx.guild.id}"][config] = value
        with open("Data/server_config.json", "w") as file:
            json.dump(server_config, file, indent=4)
        await ctx.reply(f"Set {config} to {bool(value)}", ephemeral=True)

    @configure.autocomplete("config")
    async def config_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        choices = ["Games in Thread", "Edit Game Message", "Log Moves", "Delete Thread after Game", "Reset All"]
        return [
            app_commands.Choice(name=choice, value="_".join(choice.lower().split()))
            for choice in choices if current.lower() in choice.lower()
        ]
    
    @configure.autocomplete("value")
    async def bool_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        choices = {
            "true": 1,
            "false": 0,
            "1": 1,
            "0": 0
        }

        return [
            app_commands.Choice(name=k, value=v)
            for k, v in choices.items()
            if current.lower() in k
        ]

async def setup(bot):
    await bot.add_cog(KnucklebonesCog(bot))