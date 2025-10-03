from discord.ext import commands

class ReloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="reload", description="Reruns the bot's setup hook.")
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

    @commands.hybrid_command(name="reload_no_sync", description="Reruns the bot's setup hook without syncing commands.", alias=["reload_nosync", "reload_without_sync"])
    @commands.check_any(commands.is_owner())
    async def reload_no_sync(self, ctx: commands.Context):
        """Runs the setup hook from the bot's class without syncing commands."""
        try:
            msg = await ctx.reply("Reloading without syncing...", ephemeral=False)
            await self.bot.unload_cogs()
            await self.bot.setup_without_sync()
            await msg.edit(content="Reloaded successfully without syncing!")
        except Exception as e:
            await ctx.send(f"An error occurred while running the setup hook without syncing: {e}")

async def setup(bot):
    await bot.add_cog(ReloadCog(bot))