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
import discord
from discord.ext import commands
from jishaku.paginators import PaginatorEmbedInterface as PEI
from jishaku.paginators import PaginatorInterface as PI

from guildmanager.io import read


class GMcog(commands.Cog, name="Guild Management Cog"):
	"""Guild Management (GM for short) is a module and cog that is used for managing a bot's guilds.

	Read about it at the readme: https://github.com/dragdev-studios/guildmanager/blob/master/README.md"""
	def __init__(self, bot):
		if bot.is_ready():
			if not bot.user.bot:
				raise TypeError("GMcog, __init__, bot: bot is not an actual bot but instead a Client, probably selfbot."
								" GM does not work with this type of account.")
			else:
				self.bot = bot
		else:
			print(f"Internal cache of bot was not loaded and Guildmanagement could not identify Type. Loaded anyway.")
			self.bot = bot
		self.data = read("./data.json", create_new=True,
						 default_new={str(self.bot.user.id): {"bans": {"users": [], "servers": {}},
															  "infractions": {},
															  "newserverchannel": None,
															  "serverleavechannel": None,
															  "newservermessage": "Joined server {0.name}.",
															  "leaveservermessage": "Left server {0.name} (`{0.id}`).",
															  "maxservers": None,
															  "joinlock": False,
															  "queuejoins": False}})

	async def cog_check(self, ctx: commands.Context):
		"""The check for every command + subcommand in this cog."""
		return await ctx.bot.is_owner(ctx.author)

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
		else:
			guilds = list(sorted(guilds, key=lambda g: g.name))
		e = discord.Embed(
			title=f"Guilds: {len(guilds)}",
			description=f"New server join notification channel: "
						f"{str(self.bot.get_channel(self.data[str(self.bot.user.id)]['newserverchannel']))}\nNew server "
						f"notification:"
						f"{str(self.bot.get_channel(self.data[str(self.bot.user.id)]['newserverchannel'])).format(ctx.guild)}"
						f"\nserver leave notification channel: "
						f"{str(self.bot.get_channel(self.data[str(self.bot.user.id)]['serverleavechannel']))}\nServer leave"
						f" notification: "
						f"{str(self.bot.get_channel(self.data[str(self.bot.user.id)]['leaveservermessage']))}\n"
						f"Guild cap: {self.data[str(self.bot.user.id)]['maxservers']}\n"
						f"join lock: {self.data[str(self.bot.user.id)]['joinlock']}\n"
						f"join queue: {self.data[str(self.bot.user.id)]['queuejoins']}\n",
			color=discord.Color.blurple()
		)
		e.add_field(name="Most recently joined guild:",
					value=list(sorted(guilds, key=lambda g: g.me.joined_at, reverse=True))[0].name)
		e.add_field(name="Most recently created server:",
					value=list(sorted(guilds, key=lambda g: g.created_at, reverse=True))[0].name)
		e.add_field(name="Largest guild:",
					value=list(sorted(guilds, key=lambda g: g.member_count, reverse=True))[0].name)
		paginator = PEI if not extended else PI
		paginator = paginator(self.bot, commands.Paginator(prefix="```py", max_size=1950))
		for n, guild in enumerate(guilds, start=1):
			if extended:
				line = f"{n}. {guild.name} ({guild.id}) [{guild.owner} | {guild.owner_id}]"
				await paginator.add_line(line)
			else:
				line = f"{n}. {guild.name}"
				await paginator.add_line(line)
		await ctx.send(embed=e, delete_after=60*30)
		await paginator.send_to(ctx.channel)


def setup(bot):
	try:
		for cmd in set(GMcog(bot).walk_commands()):
			bot.remove_command(cmd.name)
			for alias in cmd.aliases:
				bot.remove_command(alias)
		bot.add_cog(GMcog(bot))
	except TypeError as error:
		raise commands.ExtensionNotLoaded from error
	except commands.ExtensionFailed as orig:
		try:
			bot.add_cog(GMcog(bot))
		except Exception as f:
			raise Exception from f
	except Exception as unknownerror:
		raise commands.ExtensionError from unknownerror
