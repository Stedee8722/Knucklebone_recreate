from discord.ext import commands

class HelpCommand(commands.Cog, name="help_command"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="help", with_app_command=True, description="How to use my commands.")
    async def help(self, ctx: commands.Context):
        await ctx.reply(f'Type out /knucklebones and pick your opponent', ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(HelpCommand(bot))