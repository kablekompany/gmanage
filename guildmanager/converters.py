import datetime

from discord import Guild
from discord.ext import commands


class FuzzyGuild(commands.Converter):
    """Returns a guild based on ID, name, or owner ID

    :returns discord.Guild:"""

    async def convert(self, ctx: commands.Context, argument: str) -> Guild:
        # stolen from my classic "DynamicGuild" Class some may have seen used before.
        try:
            argument = int(argument)
        except:
            pass
        bot = ctx.bot
        if isinstance(argument, int):
            # check if its an ID first, else check enumerator
            guild = bot.get_guild(argument)
            if guild is not None:  # YAY
                return guild
            else:  # AWW
                for number, guild in enumerate(bot.guilds, start=1):
                    if number == argument:
                        return guild
                else:
                    if guild is None:
                        raise commands.BadArgument(f"Could not convert '{argument}' to 'Guild' with reason 'type None'")
                    else:
                        raise commands.BadArgument(f"Could not convert '{argument}' to 'Guild' as loop left.")
        elif isinstance(argument, str):  # assume its a name
            for guild in bot.guilds:
                if guild.name.lower() == argument.lower():
                    return guild
            else:
                raise commands.BadArgument(f"Could not convert '{argument}' to 'Guild' with reason 'type None' at 1")
        else:
            raise commands.BadArgument(f"Could not convert argument of type '{type(argument)}' to 'Guild'")


def ago_time(time):
    """Convert a time (datetime) to a human readable format."""
    date_join = datetime.datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S.%f")
    date_now = datetime.datetime.now(datetime.timezone.utc)
    date_now = date_now.replace(tzinfo=None)
    since_join = date_now - date_join

    m, s = divmod(int(since_join.total_seconds()), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    y = 0
    while d >= 365:
        d -= 365
        y += 1

    if y > 0:
        msg = "{4}y, {0}d {1}h {2}m {3}s ago"
    elif d > 0 and y == 0:
        msg = "{0}d {1}h {2}m {3}s ago"
    elif d == 0 and h > 0:
        msg = "{1}h {2}m {3}s ago"
    elif d == 0 and h == 0 and m > 0:
        msg = "{2}m {3}s ago"
    elif d == 0 and h == 0 and m == 0 and s > 0:
        msg = "{3}s ago"
    else:
        msg = ""
    return msg.format(d, h, m, s, y)
