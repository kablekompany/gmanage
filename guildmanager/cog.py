"""
Copyright 2020 DragDev Studios

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
import os
import subprocess
from datetime import datetime

import discord
from discord.ext import commands
from jishaku.paginators import PaginatorEmbedInterface as PEI
from jishaku.paginators import PaginatorInterface as PI

from guildmanager import __version__
from guildmanager.converters import FuzzyGuild
from guildmanager.io import read, write


class GMcog(commands.Cog, name="Guild Management Cog"):
	"""Guild Management (GM for short) is a module and cog that is used for managing a bot's guilds.

	Read about it at the readme: https://github.com/dragdev-studios/guildmanager/blob/master/README.md"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.data = read("./guildmanager.data", create_new=True,
						 default_new={"bans": {"users": [], "servers": {}},
									  "infractions": {},
									  "newserverchannel": None,
									  "serverleavechannel": None,
									  "newservermessage": "Joined server {0.name}.",
									  "leaveservermessage": "Left server {0.name} (`{0.id}`).",
									  "maxservers": None,
									  "joinlock": False,
									  "queuejoins": False, "first run": True,
									  "git ver": str(subprocess.check_output(["git",
																			  "rev-parse",
																			  "HEAD"])).strip()
									  })

	def cog_unload(self):
		write("./guildmanager.data", self.data, indent=2, rollback=True)

	async def cog_check(self, ctx: commands.Context):
		"""The check for every command + subcommand in this cog."""
		return await ctx.bot.is_owner(ctx.author) and ctx.bot.user.bot

	@commands.group(name="guilds", aliases=["servers", "gm", "GuildManagement"], case_insensitive=True,
					invoke_without_command=True)
	@commands.bot_has_permissions(embed_links=True, send_messages=True, read_messages=True, external_emojis=True,
								  manage_messages=True, read_message_history=True)
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
		e = discord.Embed(
			title=f"Guilds: {len(guilds)}",
			color=discord.Color.blurple()
		)
		e.add_field(name="Cog Settings:", value=f"New server join notification channel: "
												f"{str(self.bot.get_channel(self.data['newserverchannel']))}\nNew server "
												f"notification:"
												f"{str(self.bot.get_channel(self.data['newserverchannel'])).format(ctx.guild)}"
												f"\nserver leave notification channel: "
												f"{str(self.bot.get_channel(self.data['serverleavechannel']))}\nServer leave"
												f" notification: "
												f"{str(self.bot.get_channel(self.data['leaveservermessage']))}\n"
												f"Guild cap: {self.data['maxservers']}\n"
												f"join lock: {self.data['joinlock']}\n"
												f"join queue: {self.data['queuejoins']}\n",
					inline=False)
		e.add_field(name="Most recently joined guild:",
					value=list(sorted(guilds, key=lambda g: g.me.joined_at, reverse=True))[0].name)
		e.add_field(name="Most recently created server:",
					value=list(sorted(guilds, key=lambda g: g.created_at, reverse=True))[0].name)
		e.add_field(name="Largest guild:",
					value=list(sorted(guilds, key=lambda g: g.member_count, reverse=True))[0].name)
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
			write("./guildmanager.data", self.data, rollback=True)
		else:
			m = await ctx.send(f"Banning {guild.name} (`{guild.id}`) for reason {reason[:1700]}...", delete_after=30)
			try:
				await guild.owner.send(f"Your guild **{guild.name}** Has been banned from using this bot, with reason:"
				                       f"\n{reason[:1700]}.")
			except discord.Forbidden:
				pass
			finally:
				await guild.leave()
				write("./guildmanager.data", data=self.data, rollback=True)
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
			invites = await guild.invites()
			return await ctx.send(f"Invite: <{invites[0].url}>", delete_after=10)
		else:
			for channel in guild.channels:
				if channel.permissions_for(guild.me).create_instant_invite:
					i = await channel.create_invite(
						max_age=120,
						max_uses=5,
						reason=f"{ctx.prefix}guilds invite {guild.name} used by my owner to generate an invite."
					)
					return await ctx.send(f"2 minute invite: {i.url}", delete_after=60)
			else:
				return await ctx.send(f"Unable to get or generate an invite (missing permissions).", delete_after=10)

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
		if str(guild.id) in self.data[str(guild.me.id)]["bans"]["servers"].keys():
			reason = self.data[str(guild.me.id)]["bans"]["servers"][str(guild.id)]
			try:
				await guild.owner.send(
					f"Your guild, **{guild.name}** has been banned from using this bot (with the reason '{reason}'.). Contact a developer"
					" to see if you can appeal this.")
			except discord.Forbidden:
				pass

	@commands.group(name="guildmanager", invoke_without_command=True, aliases=['gmeta', 'gman', 'gmd'])
	async def gmroot(self, ctx: commands.Context):
		"""
		meta commands relating to the guildmanager module itself.
		without a subcommand this returns basic information.
		"""
		since = datetime(2020, 3, 15, 23, 50, 34, 0)
		try:
			last_commit = str(subprocess.check_output(["git", "rev-parse", "HEAD"]))
		except FileNotFoundError as fnfe:
			return await ctx.send(
				f"Unable to get last version - git is not installed. Unless you directly installed the"
				f" module or removed git recently, this error should __never__ raise.")
		e = discord.Embed(
			title=f"GuildManager - version {__version__} [commit {str(last_commit[:7]).encode('utf-8')}]",
			description=f"You seem lost. Try `{ctx.prefix}help {ctx.command.qualified_name}`.",
			color=discord.Color.blue(),
			timestamp=since
		)
		if float(str(__version__)[3:5]) > 3.3:
			try:
				cur = self.data["git ver"]

				if cur != last_commit:
					footer = f"Your module is out of date! Commit {last_commit[:7]} is available, and you're on {self.data['git ver']}."
				else:
					footer = f"Your module is up to date!"
			except KeyError:
				footer = f"Unable to determine if module is up to date because " \
						 f"`guildmanager.data` file lacks the `git ver` key. Please fix this, re-installing the module" \
						 f" will help."
		else:
			footer = f"Your module is out of date, and the git hash could not be determined."
		e.set_footer(text=footer + " | Live since ")
		await ctx.send(embed=e)

	@gmroot.command(name="update")
	async def gm_update(self, ctx: commands.Context):
		"""[optionally force] updates the module automatically."""
		self.data["git ver"] = str(subprocess.check_output(["git", "rev-parse", "HEAD"])).encode("utf-8")
		await ctx.message.delete(delay=30)
		url = "https://github.com/dragdev-studios/guildmanager"
		cmd = "python -m pip install git+{url} --upgrade --user"
		res = os.system(cmd)
		if res not in [0, 256]:
			return await ctx.send(
				f"Something went wrong while updating (cmd returned code other than 0(win32) or 256(linux). Please"
				f" update manually with command `{cmd}`. `returned: {res}`", delete_after=30)
		else:
			await asyncio.sleep(8)  # testing reveals on average its 7 seconds on a 93mbps download speed to update.
			try:
				self.bot.reload_extension("guildmanager.cog")
			except Exception as e:
				await ctx.send(f"Error reloading updated module: `{str(e)}`. Traceback has been raised. If this issue"
							   f" persists, please open an issue at {url}/issues/new.\n\nSee: "
							   f"<{url}/issues/6>", delete_after=30)
				raise commands.ExtensionFailed from e
			else:
				return await ctx.send(f"Successfully reloaded.", delete_after=10)

	@gmroot.command(name="repair")
	async def gm_fix(self, ctx: commands.Context):
		"""Fixes issues with the data.json file."""
		msg = await ctx.send(f"Attempting to write default data...")
		try:
			self.data = read("./guildmanager.data", create_new=True,
							 default_new={"bans": {"users": [], "servers": {}},
										  "infractions": {},
										  "newserverchannel": None,
										  "serverleavechannel": None,
										  "newservermessage": "Joined server {0.name}.",
										  "leaveservermessage": "Left server {0.name} (`{0.id}`).",
										  "maxservers": None,
										  "joinlock": False,
										  "queuejoins": False, "first run": True,
										  "git ver": str(subprocess.check_output(["git",
																				  "rev-parse",
																				  "HEAD"])).strip()
										  })
			return await msg.edit(content="Fixed.")
		except:
			await msg.edit(content="Creating new file.")
			self.data = write("./guildmanager.data", {"bans": {"users": [], "servers": {}},
													  "infractions": {},
													  "newserverchannel": None,
													  "serverleavechannel": None,
													  "newservermessage": "Joined server {0.name}.",
													  "leaveservermessage": "Left server {0.name} (`{0.id}`).",
													  "maxservers": None,
													  "joinlock": False,
													  "queuejoins": False, "first run": True,
													  "git ver": str(
														  subprocess.check_output(["git",
														                           "rev-parse",
														                           "HEAD"])).strip()
			                                          })
			await msg.edit(content=f"Fixed.")

	@commands.Cog.listener(name="on_command_completion")
	async def del_our_msgs(self, ctx: commands.Context):
		if ctx.command.cog.qualified_name == "Guild Management Cog":
			if ctx.channel.permissions_for(ctx.me).manage_messages:
				await ctx.message.delete(delay=60)


def setup(bot):
	try:
		for cmd in set(GMcog(bot).walk_commands()):
			bot.remove_command(cmd.name)
			for alias in cmd.aliases:
				bot.remove_command(alias)
		bot.add_cog(GMcog(bot))
	except TypeError as error:
		raise commands.ExtensionNotLoaded from error
	except Exception as unknownerror:
		raise commands.ExtensionError from unknownerror
