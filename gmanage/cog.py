"""
Copyright 2020 KableKompany 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
import json
import os
import traceback
from datetime import datetime
from typing import Union

import discord
from jishaku.paginators import PaginatorEmbedInterface as PEI
from jishaku.paginators import PaginatorInterface as PI
from matplotlib import pyplot as plt

# from discord.ext import commands
from redbot.core import commands

from gmanage import __version__
from gmanage.converters import FuzzyGuild
from gmanage.io import read, write


class GMcog(commands.Cog, name="Guild Management Cog"):
    """Guild Management (GM for short) is a module and cog that is used for managing a bot's guilds.

    Read about it at the readme: https://github.com/kablekompany/gmanage/blob/master/README.md"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = read(
            "./gmanage.data",
            create_new=True,
            default_new={
                "bans": {"users": [], "servers": {}},
                "infractions": {},
                "newserverchannel": None,
                "serverleavechannel": None,
                "maxservers": None,
                "joinlock": False,
                "queuejoins": False,
                "first run": True,
            },
        )

    def cog_unload(self):
        write("./gmanage.data", self.data, indent=2, rollback=True)

    async def cog_check(self, ctx: commands.Context):
        """The check for every command + subcommand in this cog."""
        return await ctx.bot.is_owner(ctx.author) and ctx.bot.user.bot

    @commands.group(
        name="guilds", aliases=["servers", "gm", "GuildManagement"], case_insensitive=True, invoke_without_command=True
    )
    @commands.bot_has_permissions(
        embed_links=True,
        send_messages=True,
        read_messages=True,
        external_emojis=True,
        read_message_history=True,
    )
    async def guilds_root(self, ctx: commands.Context, *flags):
        """
        Lists all servers. Pretty simple. To see a list of every command, run [p]help guilds.

        `:flags:` are a list of command-line style flags (below), separated by spaces.
        Flags:
          * `--extended`: Shows extended information format (#. name (ID) [Owner Name | Owner ID])
          * `--sort-by-join-recent`: Sorts list by guilds joined from most recent to oldest join.
          * `--sort-by-join-oldest`: Reverse of recent.
          * `--sort-by-created-recent`: Sorts by guild age, youngest to oldest.
          * `--sort-by-created-oldest`: inverse of recent.
          * `--sort-by-members`: Sorts by member count, largest to smallest.
          * `--sort-by-bots`: Sorts by bot count, most to least.
          * `--sort-to-enum`: Sorts to default order, so you can use their enum IDs in commands like guilds invite <num>
        Flags do stack, so you can do things like `[p]guilds --extended --sort-by-bots --sort-by-recent`
        There are no restrictions, so you can use every flag if you want. However this would be very contradicting.
        All flags are processed in the above order, starting with `--extended` to `--sort-by-bots`.
        """
        # await ctx.send(
        #     f":exclamation: Notice from developer: **gmanage is deprecated.** Please stop using it,"
        #     f" as it is no-longer maintained."
        # )
        flags = [fl.lower() for fl in flags if fl.startswith("--")]
        guilds = self.bot.guilds
        extended = "--extended" in flags or "-e" in flags
        if flags:
            if "--sort-by-join-recent" in flags or "-sbjr" in flags:
                guilds = list(sorted(guilds, key=lambda g: g.me.joined_at, reverse=True))
            if "--sort-by-join-oldest" in flags or "-sbjo" in flags:
                guilds = list(sorted(guilds, key=lambda g: g.me.joined_at))
            if "--sort-by-created-recent" in flags or "-sbcr" in flags:
                guilds = list(sorted(guilds, key=lambda g: g.created_at, reverse=True))
            if "--sort-by-created-oldest" in flags or "-sbco" in flags:
                guilds = list(sorted(guilds, key=lambda g: g.created_at))
            if "--sort-by-members" in flags or "-sbm" in flags:
                guilds = list(sorted(guilds, key=lambda g: g.member_count, reverse=True))
            if "--sort-by-bots" in flags or "-sbb" in flags:
                guilds = list(sorted(guilds, key=lambda g: len([m for m in g.members if m.bot]), reverse=True))
            if "--sort-to-enum" in flags or "-ste" in flags:
                guilds = self.bot.guilds
        else:
            guilds = list(sorted(guilds, key=lambda g: g.name))
        e = discord.Embed(title=f"Guilds: {len(guilds)}", color=discord.Color.blurple())
        try:
            e.add_field(
                name="Cog Settings:",
                value=f"New server join notification channel: "
                f"{str(self.bot.get_channel(self.data['newserverchannel']))}\nNew server "
                f"notification:"
                f"{str(self.bot.get_channel(self.data['newserverchannel'])).format(ctx.guild)}"
                f"\nserver leave notification channel: "
                f"{str(self.bot.get_channel(self.data['serverleavechannel']))}\nServer leave"
                f" notification: "
                f"Guild cap: {self.data['maxservers']}\n"
                f"join lock: {self.data['joinlock']}\n"
                f"join queue: {self.data['queuejoins']}\n",
                inline=False,
            )
        except KeyError:
            pass
        e.add_field(
            name="Most recently joined guild:",
            value=list(sorted(guilds, key=lambda g: g.me.joined_at, reverse=True))[0].name,
        )
        e.add_field(
            name="Most recently created server:",
            value=list(sorted(guilds, key=lambda g: g.created_at, reverse=True))[0].name,
        )
        e.add_field(
            name="Largest guild:", value=list(sorted(guilds, key=lambda g: g.member_count, reverse=True))[0].name
        )
        paginator = PEI if not extended else PI
        paginator = paginator(self.bot, commands.Paginator(prefix="```py", max_size=1950), embed=e)
        for n, guild in enumerate(guilds, start=1):
            if extended:
                line = f"{n}. {guild.name} ({guild.id}) [{guild.owner} | {guild.owner_id}]"
                await paginator.add_line(line)
            else:
                line = f"{n}. {guild.name}"
                await paginator.add_line(line)
        # await ctx.send(embed=e, delete_after=60 * 30)
        await paginator.send_to(ctx.channel)

    @guilds_root.command()
    async def ban(self, ctx: commands.Context, guild: FuzzyGuild(), *, reason: str = "No Reason."):
        """Bans a server from using the bot

        Every time the bot joins a banned guild, it leaves it
        If the bot finds it is in a server that is banned, usually when the guild gets an update, it will leave.
        If guild is already banned, will unban it.

        guild can be the server's ID, name, or enum ID (the number shown before the name in [p]guilds)"""
        guild: discord.Guild  # linting
        if self.data["bans"]["servers"].get(str(guild.id)):
            await ctx.send(f"Unbanned {guild.name} (`{guild.id}`).", delete_after=30)
            del self.data["bans"]["servers"][str(guild.id)]
            write("./gmanage.data", self.data, rollback=True)
        else:
            m = await ctx.send(f"Banning {guild.name} (`{guild.id}`) for reason {reason[:1700]}...", delete_after=30)
            try:
                await guild.owner.send(
                    f"Your guild **{guild.name}** Has been banned from using this bot, with reason:"
                    f"\n{reason[:1700]}."
                )
            except discord.Forbidden:
                pass
            finally:
                await guild.leave()
                write("./gmanage.data", data=self.data, rollback=True)
                return await m.edit(content=f"Banned {guild.name}.")

    @guilds_root.command(name="invite")
    async def guilds_invite(self, ctx: commands.Context, *, guild: FuzzyGuild()):
        """Returns an invite to specified Guild.

        Tries to get invites currently available. If it fails to, it will simply try and create one."""
        guild: discord.Guild
        if "VANITY_URL" in guild.features:
            i = await guild.vanity_invite()
            return await ctx.send(f"Vanity Invite: <{i.url}>", delete_after=10)
        if guild.me.guild_permissions.manage_guild:
            m = await ctx.send("Attempting to find an invite.")
            invites = await guild.invites()
            for invite in invites:
                if invite.max_age == 0:
                    return await m.edit(content=f"Infinite Invite: {invite}")
            else:
                await m.edit(content="No Infinite Invites found - creating.")
                for channel in guild.text_channels:
                    try:
                        invite = await channel.create_invite(
                            max_age=60,
                            max_uses=1,
                            unique=True,
                            reason=f"Invite requested"
                            f" by {ctx.author} via official management command. do not be alarmed, this is usually just"
                            f" to check something.",
                        )
                        break
                    except:
                        continue
                else:
                    return await m.edit(content=f"Unable to create an invite - missing permissions.")
                await m.edit(content=f"Temp invite: {invite.url} -> max age: 60s, max uses: 1")
        else:
            m = await ctx.send("Attempting to create an invite.")
            for channel in guild.text_channels:
                try:
                    invite = await channel.create_invite(
                        max_age=60,
                        max_uses=1,
                        unique=True,
                        reason=f"Invite requested"
                        f" by {ctx.author} via official management command. do not be alarmed, this is usually just"
                        f" to check something.",
                    )
                    break
                except:
                    continue
            else:
                return await m.edit(content=f"Unable to create an invite - missing permissions.")
            await m.edit(content=f"Temp invite: {invite.url} -> max age: 60s, max uses: 1")

    @guilds_root.command(name="leave")
    async def guilds_leave(self, ctx: commands.Context, *, guild: FuzzyGuild() = None):
        """Leaves a guild. Just that.
        Leave guild blank to default to this guild."""
        guild = guild or ctx.guild
        await guild.leave()
        await ctx.author.send(f"Left guild {guild.name}.")

    @commands.Cog.listener(name="on_guild_join")
    @commands.Cog.listener(name="on_guild_update")
    async def check_guild_banned(self, guild: discord.Guild, extra: discord.Guild = None):
        """Checks if a guild is banned, on guild update and on guild join. This also picks up the custom
        event "on_guild_ban"

        This dispatches an event called "banned_guild_leave", which you can do whatever with as a regular listener
        (e.g @commands.Cog.listen(name="on_banned_guild_leave"))
        does NOT trigger `guild leave` notification.
        """
        # we leave `extra` there for on_guild_update, where we dont really need it. And to prevent Missing arg errors,
        # we make it optional
        if str(guild.id) in self.data["bans"]["servers"].keys():
            reason = self.data["bans"]["servers"][str(guild.id)]
            try:
                await guild.owner.send(
                    f"Your guild, **{guild.name}** has been banned from using this bot (with the reason '{reason}'.). Contact a developer"
                    " to see if you can appeal this."
                )
            except discord.Forbidden:
                pass

    @guilds_root.command(name="mutual")
    async def mutual_guilds(self, ctx: commands.Context, *, user: Union[discord.User, FuzzyGuild]):
        """Lists all mutual guilds you have with :user:
        if user is a guild, it will default to the guild's owner."""
        if isinstance(user, discord.User):
            user: discord.User
            user = user
        else:
            user: discord.Guild
            user = user.owner
        guilds = [g for g in self.bot.guilds if g.get_member(user.id)]
        e = discord.Embed(title=f"Mutual guilds: {len(guilds)}", color=discord.Color.blue())
        paginator = PEI(self.bot, commands.Paginator(prefix="```md", max_size=1900), embed=e)
        for guild in guilds:
            await paginator.add_line(f"• {guild.name} ({guild.id})")
        await paginator.send_to(ctx.channel)

    @guilds_root.command(name="growth")
    async def gr(self, ctx: commands.Context, dt: str = None):
        """Displays a graph of server growth

        dt can either be in the format of `d/m/YYYY`, `m/YYYY` or `m/yy`. Leave blank to get from start of bot to now."""
        import io

        if dt:
            formats = ["%d/%m/%Y", "%m/%Y", "%m/%y"]
            for f0rmat in formats:
                try:
                    period: datetime = datetime.strptime(dt, f0rmat)
                except ValueError:
                    continue
                else:
                    guilds = [
                        guild.me.joined_at
                        for guild in self.bot.guilds
                        if guild.me.joined_at
                        and guild.me.joined_at
                        and guild.me.joined_at.month == period.month
                        and guild.me.joined_at.year == period.year
                    ]
                    guilds.sort(key=lambda g: g)
                    inmonth = 30 if period.month % 2 else 31
                    perday = round(len(guilds) / inmonth, 3)
                    plt.grid(True)
                    fig, ax = plt.subplots()

                    ax.plot(guilds, tuple(range(len(guilds))), lw=2)

                    fig.autofmt_xdate()

                    plt.xlabel("Date")
                    plt.ylabel("Guilds")
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png")
                    buf.seek(0)
                    e = discord.Embed(
                        description=f"Total guilds from {guilds[0].day}/{period.month}/{period.year} to {guilds[-1].day}/"
                        f"{period.month}/{period.year}: {len(guilds)}. That is {perday} guilds per day."
                    )
                    e.set_image(url="attachment://growth.png")
                    await ctx.send(embed=e, file=discord.File(buf, filename="growth.png"))
                    buf.close()
                    plt.close()
                    return
            else:
                return await ctx.send("Unable to convert to any time.")
        else:
            guilds = [guild.me.joined_at for guild in self.bot.guilds if guild.me.joined_at and guild.me.joined_at]
            guilds.sort(key=lambda g: g)
            months = {}
            for joined in guilds:
                if months.get(joined.month):
                    pass
            perday = round(len(guilds) / 365, 3)
            permonth = round(len(guilds) / 12, 3)
            plt.grid(True)
            fig, ax = plt.subplots()

            ax.plot(guilds, tuple(range(len(guilds))), lw=2, label="server count")

            fig.autofmt_xdate()

            plt.xlabel("Date")
            plt.ylabel("Guilds")
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            e = discord.Embed(
                description=f"Total guilds: {len(guilds)}.\nThat is {perday} guilds per year, and {permonth} guilds "
                f"per month"
            )
            e.set_image(url="attachment://growth.png")
            await ctx.send(embed=e, file=discord.File(buf, filename="growth.png"))
            buf.close()
            plt.close()

    @commands.group(name="gmanage", invoke_without_command=True, aliases=["gmeta", "gman", "gmd"])
    async def gmroot(self, ctx: commands.Context):
        """
        meta commands relating to the gmanage module itself.
        without a subcommand this returns basic information.
        """
        since = datetime(2020, 3, 15, 23, 50, 34, 0)
        last_update = datetime(2020, 4, 10, 15, 16, 0, 0)
        e = discord.Embed(
            title=f"GManage - version {__version__}",
            description=f"Last Updated: {str(last_update)}\nYou seem lost. Try `{ctx.prefix}help {ctx.command.qualified_name}`.",
            color=discord.Color.blue(),
            timestamp=since,
        )
        e.set_footer(text="Live since ")
        await ctx.send(embed=e)

    @gmroot.command(name="update")
    async def gm_update(self, ctx: commands.Context, *, pythoncommand: str = "python3"):
        """[optionally force] updates the module automatically.

        `pythoncommand` should be the command used to invoke python. This defaults to python3 (unix OSes),
        but if you are on, for example, windows, you should run `[prefix]gman update py`."""
        await ctx.message.delete(delay=30)
        await ctx.channel.trigger_typing()
        url = "https://github.com/kablekompany/gmanage"
        cmd = f"{pythoncommand} -m pip install git+{url} --upgrade"
        res = os.system(cmd)
        if res not in [0, 256]:
            return await ctx.send(
                f"Something went wrong while updating (cmd returned code other than 0(win32) or 256(linux). Please"
                f" update manually with command `{cmd}`. `returned: {res}`",
                delete_after=30,
            )
        else:
            await asyncio.sleep(8)  # testing reveals on average its 7 seconds on a 93mbps download speed to update.
            try:
                self.bot.reload_extension("gmanage.cog")
            except Exception as e:
                await ctx.send(
                    f"Error reloading updated module: `{str(e)}`. Traceback has been raised. If this issue"
                    f" persists, please open an issue at {url}/issues/new.\n\nSee: "
                    f"<{url}/issues/6>",
                    delete_after=30,
                )
                raise commands.ExtensionFailed("gmanage", e) from e
            else:
                return await ctx.send(f"Successfully reloaded.", delete_after=10)

    @gmroot.command(name="repair")
    async def gm_fix(self, ctx: commands.Context):
        """Fixes issues with the data.json file."""
        msg = await ctx.send(f"Attempting to write default data...")
        try:
            self.data = read(
                "./gmanage.data",
                create_new=True,
                default_new={
                    "bans": {"users": [], "servers": {}},
                    "infractions": {},
                    "newserverchannel": None,
                    "serverleavechannel": None,
                    "maxservers": None,
                    "joinlock": False,
                    "queuejoins": False,
                    "first run": True,
                },
            )
            return await msg.edit(content="Fixed.")
        except:
            await msg.edit(content="Creating new file.")
            self.data = write(
                "./gmanage.data",
                {
                    "bans": {"users": [], "servers": {}},
                    "infractions": {},
                    "newserverchannel": None,
                    "serverleavechannel": None,
                    "maxservers": None,
                    "joinlock": False,
                    "queuejoins": False,
                    "first run": True,
                },
            )
            await msg.edit(content=f"Fixed.")

    @gmroot.group(name="set", invoke_without_command=True)
    async def gmset(self, ctx: commands.Context):
        """This command shows your current settings. Use subcommands to change them."""
        await ctx.send(f"Warning: gmset and subcommands are not complete and no support is available yet.")

        def batch(iterable: str, size: int = 1700):
            for i in range(0, len(iterable), size):
                yield tuple(iterable[i : i + size])

        await ctx.send(f"Work in progress. For now, here's the raw JSON: ", delete_after=300)
        paginator = commands.Paginator(prefix="```json")
        for line in json.dumps(self.data, indent=2).splitlines():
            if len(line) > 1980:
                for newline in batch(line):
                    paginator.add_line("".join(newline))
            else:
                paginator.add_line(line)
        for page in paginator.pages:
            await ctx.send(page, delete_after=300)
            await asyncio.sleep(1)

    @gmset.command(name="maxservers", aliases=["maximumservers", "maxguilds", "maximumguilds"])
    async def gmset_maxservers(self, ctx: commands.Context, *, total: int = None):
        """Sets how many servers you're allowing to use your bot. Leave `total` blank to disable.

        This does not affect how many servers your bot is already in."""
        self.data["maxservers"] = total
        write("./gmanage.data", self.data)
        return await ctx.send(f"Set your max guild count to {total if total is not None else 'Off'}.")

    @gmset.command(name="newserverchannel", aliases=["newnotificationchannel", "newservernotifchan", "nsc", "nsnc"])
    async def gmset_newchannel(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        """Sets the channel where messages will be sent when your bot joins a new server.

        The message sent can be configured via `[prefix]gman set newservermsg`.

        leave `channel` blank to disable it."""
        self.data["newserverchannel"] = channel.id if channel else None
        write("./gmanage.data", self.data)
        return await ctx.send(
            f"Set your New server notification channel to {channel.mention if channel is not None else 'Off'}."
        )

    # @gmset.command(name="newservermsg", aliases=["newnotification", "newservernotif", "nsn"], enabled=False)
    # async def gmset_newnotif(self, ctx: commands.Context, *, message: str):
    #     """Sets the new server notification message.

    #     if the message starts with `{` and ends with `}`, it is presumed to be a dictionary which contains data for an
    #     embed."""
    #     if message.startswith("{") and message.endswith("}"):
    #         try:
    #             data = json.loads(message)
    #         except:
    #             fmt = traceback.format_exc()

    @gmset.command(name="guildleave")
    async def gmset_leavechannel(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        """Sets the channel where messages will be sent when your bot leaves a server.

        The message sent can be configured via `[prefix]gman set guildleave`.

        leave `channel` blank to disable it."""
        self.data["serverleavechannel"] = channel.id if channel else None
        write("./gmanage.data", self.data)
        return await ctx.send(
            f"Set your New server notification channel to {channel.mention if channel is not None else 'Off'}."
        )

    @commands.Cog.listener(name="on_command_completion")
    async def del_our_msgs(self, ctx: commands.Context):
        if ctx.command.cog is not None and ctx.command.cog.qualified_name == "Guild Management Cog":
            if ctx.channel.permissions_for(ctx.me).manage_messages:
                await ctx.message.delete(delay=60)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if self.data["newserverchannel"]:
            try:
                channel = self.bot.get_channel(int(self.data["newserverchannel"]))
            except ValueError as e:
                raise ValueError("newserverchannel, serverleavechannel and max servers must be integers!") from e
            embed = discord.Embed()
            embed.add_field(
            name=guild.name.format(guild, self.bot, channel),
            value=guild.value,
            inline=True,
            )
            embed.set_footer(
                text=embed.footer.format(guild, self.bot, channel), icon_url=embed.footer.icon_url
                )
            embed.title.format(guild, self.bot, channel)
            embed.description.format(guild, self.bot, channel)
            # if embed.title:
            #     embed.title.format(guild, self.bot, channel)
            # if embed.description:
            #     embed.description.format(guild, self.bot, channel)
            # if embed.footer:
            #     embed.set_footer(
            #     text=embed.footer.format(guild, self.bot, channel), icon_url=embed.footer.icon_url
            #     )
            try:
                await channel.send(embed=embed)
            except:
                raise
                #     try:
                #     except Exception as e:
                #         raise TypeError(
                #             "an error was raised in the process of creating an embed from the provided"
                #             " dict."
                #         ) from e
                #     else:
                #         # old = embed.fields
                        # embed.clear_fields()
                        # for i, field in enumerate(old):
                        #     embed.add_field(
                        #         name=old[i].name.format(guild, self.bot, channel),
                        #         value=old[i].value,
                        #         inline=old[i].inline,
                        #     )
                        # if embed.title:
                        #     embed.title.format(guild, self.bot, channel)
                        # if embed.description:
                        #     embed.description.format(guild, self.bot, channel)
                        # if embed.footer:
                        #     embed.set_footer(
                        #         text=embed.footer.format(guild, self.bot, channel), icon_url=embed.footer.icon_url
                        #     )
                        # content = None
                # else:
                #     embed = None
                # try:
                #     await channel.send(content, embed=embed)
                # except:
                #     raise

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if self.data["serverleavechannel"]:
            try:
                channel = self.bot.get_channel(int(self.data["serverleavechannel"]))
            except ValueError as e:
                raise ValueError("newserverchannel, serverleavechannel and max servers must be integers!") from e
            else:
                if isinstance(self.data["leaveservermessage"], dict):
                    try:
                        embed = discord.Embed.from_dict(self.data["leaveservermessage"])
                    except Exception as e:
                        raise TypeError(
                            "leaveservermessage was a dictionary, which is only for creating embeds, and an "
                            "an error was raised in the process of creating an embed from the provided"
                            " dict."
                        ) from e
                    else:
                        old = embed.fields
                        embed.clear_fields()
                        for i, field in enumerate(old):
                            embed.add_field(
                                name=old[i].name.format(guild, self.bot, channel),
                                value=old[i].value,
                                inline=old[i].inline,
                            )
                        if embed.title:
                            embed.title.format(guild, self.bot, channel)
                        if embed.description:
                            embed.description.format(guild, self.bot, channel)
                        if embed.footer:
                            embed.set_footer(
                                text=embed.footer.format(guild, self.bot, channel), icon_url=embed.footer.icon_url
                            )
                        content = None
                else:
                    embed = None
                    content = self.data["leaveservermessage"].format(guild, self.bot, channel)
                try:
                    await channel.send(content, embed=embed)
                except:
                    raise


def setup(bot: commands.Bot):
    if not bot.is_ready():
        print("Unable to load GManage - bot's cache is not ready, and thus would cause issues loading.")
    else:
        try:
            for cmd in set(GMcog(bot).walk_commands()):
                bot.remove_command(cmd.name)
                for alias in cmd.aliases:
                    bot.remove_command(alias)
            bot.add_cog(GMcog(bot))
        except json.JSONDecodeError:
            write(
                "./gmanage.data",
                {
                    "bans": {"users": [], "servers": {}},
                    "infractions": {},
                    "newserverchannel": None,
                    "serverleavechannel": None,
                    "maxservers": None,
                    "joinlock": False,
                    "queuejoins": False,
                    "first run": True,
                },
            )
            setup(bot)
        except TypeError as error:
            raise commands.ExtensionNotLoaded("gmanage.cog") from error
        except Exception as unknownerror:
            raise commands.ExtensionError(name="gmanage.cog") from unknownerror
