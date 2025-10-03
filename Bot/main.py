import settings, discord, os
from discord.ext import commands
import datetime

logger = settings.logging.getLogger("bot")
__version__ = "v0.0.1"
start_time = datetime.datetime.now()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix = "!", help_command=None, intents=intents)
        self.logger = logger

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/Cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await client.load_extension(f"Cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def unload_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will stop.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/Cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await client.unload_extension(f"Cogs.{extension}")
                    self.logger.info(f"Unloaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to unload extension {extension}\n{exception}"
                    )

    async def setup_hook(self) -> None:
        print("______________________________")
        print("____________Setup:____________")
        await self.load_cogs()
        guild = discord.Object(id = 1342502309929812018)
        self.tree.copy_global_to(guild = guild)
        await self.tree.sync(guild = guild)
        self.logger.info("Commands are now synced!")
        print("______________________________")

    async def setup_without_sync(self) -> None:
        print("______________________________")
        print("____________Setup:____________")
        await self.load_cogs()
        print("______________________________")

    async def on_ready(self):
        await self.wait_until_ready()
        self.logger.info(f"Now logging in as {self.user}")
        self.logger.info("Howdy! I am now online!")
        print("______________________________")
        print("_____________Logs:____________")
        activity = discord.Game(name="Ready to (T)roll!")
        #await client.change_presence(activity=activity)

    #async def on_command_error(self, ctx, error) -> None:
    #    try:
    #        await ctx.reply(f"{error}", ephemeral = True)
    #        self.logger.error(f"{error}")
    #    except Exception as error:
    #        self.logger.error(f"{error}")

if __name__ == "__main__":
    client = Bot()
    client.run(settings.TOKEN, root_logger=True)