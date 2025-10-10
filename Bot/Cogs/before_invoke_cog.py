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
        with open("Data/server_config.json", "r+") as file:
            server_config = json.load(file)
        with open("Data/server_data.json", "r+") as file:
            server_data = json.load(file)

        # flags to check if data was edited
        edited_bot_config = 0
        edited_server_config = 0

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
        bot_data_checks = ["total_used_commands", "last_reset", "total_games_played"]
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
                bot_config[check] = 0
                edited_bot_config = 1

        # server config checks
        server_config_checks = ["games_in_thread", "specified_channel", "edit_game_message", "log_moves", "delete_thread_after_game", "ephemeral_stats"]
        if f"{ctx.guild.id}" not in server_config:
            self.bot.logger.info(f"{ctx.guild.id} doesn't exist in server config. Generating...")
            server_config[f"{ctx.guild.id}"] = {}
        for check in server_config_checks:
            if check not in server_config[f"{ctx.guild.id}"]:
                self.bot.logger.info(f"{check} doesn't exist in server config for {ctx.guild.id}. Generating...")
                server_config[f"{ctx.guild.id}"][check] = 1 if check in ["games_in_thread", "log_moves", "delete_thread_after_game", "ephemeral_stats"] else 0
                edited_server_config = 1
                
        # server data checks
        server_data_checks = ["game_counter", "total_used_commands", "total_games_played"]
        if f"{ctx.guild.id}" not in server_data:
            self.bot.logger.info(f"{ctx.guild.id} doesn't exist in server data. Generating...")
            server_data[f"{ctx.guild.id}"] = {}
        for check in server_data_checks:
            if check not in server_data[f"{ctx.guild.id}"]:
                self.bot.logger.info(f"{check} doesn't exist in server data for {ctx.guild.id}. Generating...")
                server_data[f"{ctx.guild.id}"][check] = 1 if check in ["game_counter"] else 0
        if "users" not in server_data[f"{ctx.guild.id}"]:
            server_data[f"{ctx.guild.id}"]["users"] = {}
        if f"{ctx.author.id}" not in server_data[f"{ctx.guild.id}"]["users"]:
            server_data[f"{ctx.guild.id}"]["users"][f"{ctx.author.id}"] = {}
        server_data_users_checks = ["used_commands", "kb_wins", "kb_losses", "kb_games_played"]
        for check in server_data_users_checks:
            if check not in server_data[f"{ctx.guild.id}"]["users"][f"{ctx.author.id}"]:
                self.bot.logger.info(f"{check} doesn't exist in server data for {ctx.guild.id} for user {ctx.author.id}. Generating...")
                server_data[f"{ctx.guild.id}"]["users"][f"{ctx.author.id}"][check] = 0
        server_data[f"{ctx.guild.id}"]["users"][f"{ctx.author.id}"]["used_commands"] += 1
        server_data[f"{ctx.guild.id}"]["total_used_commands"] += 1

        # save changes
        # user data always changes cuz of used commands
        with open("Data/user_data.json", "w") as file:
            json.dump(user_data, file, indent=4)
        # bot data always changes cuz of used commands
        with open("Data/bot_data.json", "w") as file:
            json.dump(bot_data, file, indent=4)
        if edited_bot_config:
            with open("Data/bot_config.json", "w") as file:
                json.dump(bot_config, file, indent=4)
        if edited_server_config:
            with open("Data/server_config.json", "w") as file:
                json.dump(server_config, file, indent=4)
        with open("Data/server_data.json", "w") as file:
            json.dump(server_data, file, indent=4)

async def setup(bot) -> None:
    await bot.add_cog(BeforeInvokeCog(bot))