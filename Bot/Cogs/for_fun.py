from discord.ext import commands
from Utils import stats_util, embed_util
import json

class ForFunCog(commands.Cog, name="for_fun"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", with_app_command=True, description="Check the bot's response time!")
    async def ping(self, ctx: commands.Context):
        await ctx.reply(f"Pong! {round(self.bot.latency, 5)*1000}ms")

    #!random_stats
    @commands.hybrid_command(name="random_stats", description="Print out some useless statistics that are interesting (to me).", with_app_command=True, aliases=["random_statistics"])
    async def random_stats(self, ctx):
        await ctx.defer(ephemeral=False)
        view = stats_util.setting_option(self.bot, ctx, 0)
        with open("Data/user_data.json", "r") as file:
            user_data = json.load(file)
        with open("Data/bot_data.json", "r") as file:
            bot_data = json.load(file)
        await ctx.reply(content="", embed = await embed_util.random_stats_embed_build(ctx, 1, user_data[f"{ctx.author.id}"], bot_data["last_reset"], ctx.author.id), view = view)
        return
    
    #!kb_stats
    @commands.hybrid_command(name="knucklebones_stats", description="Get your overall server stats.", with_app_command=True, aliases=["kb_stats"])
    async def kb_stats(self, ctx):
        await ctx.defer(ephemeral=True)
        with open("Data/user_data.json", "r") as file:
            user_data = json.load(file)
        with open("Data/server_data.json", "r") as file:
            server_data = json.load(file)
        with open("Data/bot_data.json", "r") as file:
            bot_data = json.load(file)
        with open("Data/server_config.json", "r") as file:
            server_config = json.load(file)
        await ctx.reply(content="", embed = await embed_util.kb_stats_embed_build(ctx, user_data[f"{ctx.author.id}"], server_data[f"{ctx.guild.id}"]["users"][f"{ctx.author.id}"], bot_data["last_reset"], ctx.author.id), ephemeral = True if server_config[f"{ctx.guild.id}"]["ephemeral_stats"] == 1 else False)
        return

async def setup(bot) -> None:
    await bot.add_cog(ForFunCog(bot))