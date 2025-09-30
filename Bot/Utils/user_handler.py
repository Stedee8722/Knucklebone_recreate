import main, discord
from Exceptions import BotError

async def user_parser(ctx, inp:str) -> discord.User:
    """Parses a user from a mention, ID, or username.
    Args:
        ctx: The context of the command.
        inp (str): The input string to parse.
    Returns:
        discord.User: The parsed user object.
    Raises:
        BotError.ParserError: If no user is found.
    """
    try:
        if inp.startswith("<@"):
            user = await ctx.bot.fetch_user(int(inp[2:-1]))
        elif inp.isnumeric():
            user = await ctx.bot.fetch_user(int(inp))
        else:
            user = discord.utils.get(ctx.guild.members, name = inp)
        if not user:
            raise BotError.ParserError("noUser")
        return user
    except Exception as e:
        main.logger.error(e)