from discord import Embed, Colour
from discord.ext import commands
from datetime import datetime, timedelta
from Utils import user_handler
import main

async def random_stats_embed_build(ctx:commands.Context, mode:int, data:dict[str, int], last_reset, id=0) -> Embed:
    """
    Builds an embed with random statistics based on the provided mode and data.
    Args:
        ctx: The context of the command.
        mode (int): The mode for the statistics (0 for bot info, 1 for user info).
        data (dict[str, int]): The data containing statistics.
        id (int): The ID of the user if mode is 1.
        last_reset (int): The timestamp of the last reset.
    Returns:
        Embed: The constructed embed with the statistics.
    """
    if mode == 0:
        time = datetime.now() - main.start_time
        embed = Embed(title="Bot info", color=Colour.from_str("#32CD32"), description="Display name: " + ctx.bot.user.display_name + "\nUsername: " + ctx.bot.user.name + f"\nID: {ctx.bot.user.id}\nVersion: {main.__version__}\nUptime: {format_duration(time)}\nStarted at: <t:{int(main.start_time.timestamp())}:F>")

        embed.add_field(name="Total used commands", value=data["total_used_commands"])
        embed.add_field(name="Last reset", value=f"<t:{data['last_reset']}:F> (<t:{data['last_reset']}:R>)")
        embed.set_thumbnail(url=ctx.bot.user.display_avatar)
    else:
        user = await user_handler.user_parser(ctx, str(id))
        embed = Embed(title=f"User info", color=Colour.from_str("#32CD32"), description=f"User: {user.display_name}\nID: {user.id}")
        if "used_commands" in data:
            embed.add_field(name="Used commands", value=data["used_commands"])
        embed.set_thumbnail(url=user.display_avatar)
    embed.set_author(name="Random statistics")
    embed.set_footer(text=f"Requested by {ctx.author.display_name} • Started tracking on {datetime.fromtimestamp(last_reset).strftime("%d/%m/%Y %H:%M")}", icon_url=ctx.author.display_avatar)
    return embed

def format_duration(duration: timedelta) -> str:
    """Formats a timedelta into a string of the format DDD:HH:MM:SS.
    Args:
        duration (timedelta): The duration to format.
    Returns:
        str: The formatted duration string.
    """
    total_seconds = int(duration.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{days:03}:{hours:02}:{minutes:02}:{seconds:02}"