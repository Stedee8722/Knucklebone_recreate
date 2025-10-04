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
        edited_bot_config = 0

        # checks
        # user data checks
        user_data_checks = ["used_commands", "kb_wins", "kb_losses", "kb_games_played"]
        if f"{ctx.author.id}" not in user_data:
            self.bot.logger.info(f"Data for user {ctx.author.id} doesn't exist. Generating...")
            user_data[f"{ctx.author.id}"] = {}
        for check in user_data_checks:
            if check not in user_data[f"{ctx.author.id}"]:
                self.bot.logger.info(f"{check} for user {ctx.author.id} doesn't exist. Generating...")
                user_data[f"{ctx.author.id}"][check] = 0
        user_data[f"{ctx.author.id}"]["used_commands"] += 1

        # bot data checks
        bot_data_checks = ["total_used_commands", "last_reset"]
        for check in bot_data_checks:
            if check not in bot_data:
                if check == "last_reset":
                    bot_data[check] = round(datetime.datetime.now().timestamp())
                    continue
                self.bot.logger.info(f"{check} doesn't exist. Generating...")
                bot_data[check] = 0
        bot_data["total_used_commands"] += 1

        # bot config checks
        bot_config_checks = []
        for check in bot_config_checks:
            if check not in bot_config:
                self.bot.logger.info(f"{check} doesn't exist in bot config. Generating...")
                bot_config[check] = ""
                edited_bot_config = 1

        # save changes
        # user data always changes cuz of used commands
        with open("Data/user_data.json", "w") as file:
            json.dump(user_data, file, indent=4)
        # bot data always changes cuz of used commands
        with open("Data/bot_data.json", "w") as file:
            json.dump(bot_data, file, indent=4)
        if edited_bot_config == 1:
            with open("Data/bot_config.json", "w") as file:
                json.dump(bot_config, file, indent=4)

async def setup(bot) -> None:
    await bot.add_cog(BeforeInvokeCog(bot))