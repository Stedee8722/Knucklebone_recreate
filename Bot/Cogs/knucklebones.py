import discord, time
from discord.ext import commands
from discord import app_commands
from Utils import game_view, game_util, confirm_view

class KnucklebonesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="knucklebones", description="Play a game of Knucklebones!", with_app_command=True)
    @app_commands.describe(opponent="Your opponent?", uuid="(Optional) The UUID of the game you want to load.")
    async def knucklebones(self, ctx: commands.Context, opponent: discord.Member, uuid: str = None):
        await ctx.defer(ephemeral=False)
        if uuid:
            game = game_util.KnuckleboneGame.load(ctx, uuid)
            if not game:
                await ctx.reply("Can't find game!")
                return
            view = game_view.GameView(game)
            await ctx.reply(f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())
            return
        if opponent.id == ctx.bot.user.id:
            game = game_util.KnuckleboneGame(ctx.author, ctx.bot.user, True)
            game.start_game()
            view = game_view.GameView(game)
            message = await ctx.reply("Oh, you're challenging me?")
            time.sleep(2)
            await message.edit(content = f"Hey **<@{game.players[game.current_player]}>**, it's your turn! Your die is: {game.convert_value_to_emoji(game.dice, True)}", view=view, embed=game.get_embed())
            if game.current_player == 1:
                await view.start_bot_move(message)
            return
        if opponent.bot:
            return await ctx.reply("You cannot play against other bots, please against me instead!")
        view = confirm_view.ConfirmView(ctx.author, opponent)
        message = await ctx.send("", view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(KnucklebonesCog(bot))