from discord.ext import commands
import json, datetime

class BeforeInvokeCog(commands.Cog, name="before_invoke_cog"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        # open files
        with open("Data/user_data.json", "r+") as file:
            user_data = json.load(file)
        with open("Data/bot_config.json", "r+") as file:
            bot_config = json.load(file)
        with open("Data/bot_data.json", "r+") as file:
            bot_data = json.load(file)

        # flags to check if data was edited
        edited_user_data = 0
        edited_bot_data = 0
        edited_bot_config = 0

        # checks
        # user data checks
        if f"{ctx.author.id}" not in user_data:
            self.bot.logger.info(f"Data for user {ctx.author.id} doesn't exist. Generating...")
            user_data[f"{ctx.author.id}"] = {}
            edited_user_data = 1
        if "used_commands" not in user_data[f"{ctx.author.id}"]:
            self.bot.logger.info(f"Amount of commands used for user {ctx.author.id} doesn't exist. Generating...")
            user_data[f"{ctx.author.id}"]["used_commands"] = 1
            edited_user_data = 1
        else:
            user_data[f"{ctx.author.id}"]["used_commands"] += 1
            edited_user_data = 1

        # bot data checks
        if "total_used_commands" not in bot_data:
            self.bot.logger.info(f"Total amount of commands used doesn't exist. Generating...")
            bot_data["total_used_commands"] = 1
            edited_bot_data = 1
        else:
            bot_data["total_used_commands"] += 1
            edited_bot_data = 1
        if "last_reset" not in bot_data:
            self.bot.logger.info(f"Last reset doesn't exist. Generating...")
            bot_data["last_reset"] = round(datetime.datetime.now().timestamp())
            edited_bot_data = 1

        # bot config checks

        # save changes
        if edited_user_data == 1:
            with open("Data/user_data.json", "w") as file:
                json.dump(user_data, file, indent=4)
        if edited_bot_data == 1:
            with open("Data/bot_data.json", "w") as file:
                json.dump(bot_data, file, indent=4)
        if edited_bot_config == 1:
            with open("Data/bot_config.json", "w") as file:
                json.dump(bot_config, file, indent=4)

async def setup(bot) -> None:
    await bot.add_cog(BeforeInvokeCog(bot))