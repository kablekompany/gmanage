__version__ = 1
from guildmanager.cog import GMcog as GuildManager
from guildmanager.cog import setup as cogsetup

def setup(bot):
	"""Alias for cogsetup() when doing bot.load_extension"""
	cogsetup(bot)