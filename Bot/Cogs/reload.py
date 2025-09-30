from discord.ext import commands

class ReloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="reload", description="Runs the bot's setup hook.")
    @commands.check_any(commands.is_owner())
    async def reload(self, ctx: commands.Context):
        """Runs the setup hook from the bot's class."""
        try:
            msg = await ctx.reply("Reloading...", ephemeral=False)
            await self.bot.unload_cogs()
            await self.bot.setup_hook()
            await msg.edit(content="Reloaded successfully!")
        except Exception as e:
            await ctx.send(f"An error occurred while running the setup hook: {e}")

async def setup(bot):
    await bot.add_cog(ReloadCog(bot))