import discord
from discord.ext import commands
from discord import app_commands
from Utils import game_view, game_util

class KnucklebonesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="knucklebones", description="Play a game of Knucklebones!", with_app_command=True)
    @app_commands.describe(opponent="Your opponent?")
    async def knucklebones(self, ctx: commands.Context, opponent: discord.Member):
        game = game_util.KnuckleboneGame(ctx.author.id, opponent.id)
        game.start_game()
        view = game_view.GameView(game)
        await ctx.defer(ephemeral=False)
        await ctx.reply("Debug: opponent is " + str(opponent) + f" ({opponent.id})", view=view, embed=game.get_embed())

async def setup(bot):
    await bot.add_cog(KnucklebonesCog(bot))