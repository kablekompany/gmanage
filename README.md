![Python package](https://github.com/dragdev-studios/guildmanager/workflows/Python%20package/badge.svg)
# guildmanager
Simple and easy guild management for python discord bots!

#### Why this package exists
Mostly as a form of sync for our DragDev bots to use the same code (desync with the modules was a massive issue), however it seems the public 
may find this useful.

#### What is it's feature set?
It has many commands and features, some of which are listed below:
  - Nice UI for listing servers
  - Embedded Pagination
  - In-depth analytics for gathering information on servers your bot uses
  - ability to access servers (via creating an invite) or even remotely talking to users with our unique *Remote Access* chat feature.
  - banning servers, and the ability to ban every server owned by a user.
  - server infractions, and limits
  - suspicious server alerts
  - works per bot instance
  
 Much more will be coming as time moves on. Don't forget to keep the module updated!
 

#### How do I use this?
The [documentation](https://docs.dragdev.xyz/gm) explains it all.

### supporting us
You can join our [discord server](https://beta.dragdev.xyz/r/server.html) and motivate us. ~~We don't take payments or donations unless you beg us to, which is 
rather strange considering you would be begging to spend money.~~
Turns out, we do accept payments. [click here](https://beta.dragdev.xyz/donate.html)

### FAQ:
- Q: How do I make it so other users can run the guild manager's commands?
* A: use the following code snippet to subclass the cog, and change the check:
```
from guildmanager import cog
class CustomGuildManager(cog.GMcog):
    async def cog_check(self, ctx: commands.Context):
        # just a regular @commands.check() function. see: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.check
```
then instead of `bot.load_extension("guildmanager")` do `bot.load_extension("path.to.the.file")` where path.to.the.file leads to the file `CustomGuildManager` is located.
In fact, most things in the cog are subclassable. This can be useful if you want to change the ban message in `cog.py - guild_ban_check`.
## quick install:
```
# UNIX-based systems, like macos and linux distros:
python3 -m pip install git+https://github.com/dragdev-studios/guildmanager

# Windows
pip install git+https://github.com/dragdev-studios/guildmanager

-- updating --
# UNIX-based systems, like macos and linux distros:
python3 -m pip install git+https://github.com/dragdev-studios/guildmanager --upgrade

# Windows
pip install git+https://github.com/dragdev-studios/guildmanager --upgrade
```
## quick load
```
bot.load_extension("guildmanager.cog")
```

## Known issues loading:
* Please read the wiki before loading, mainly [this page](https://github.com/dragdev-studios/guildmanager/wiki/Loading-before-bot-is-ready%3F)
- [#1](https://github.com/dragdev-studios/guildmanager/issues/1) - Errors loading initially after install due to file issues [SOLVED]
- [#2](https://github.com/dragdev-studios/guildmanager/issues/2) - Errors loading before bot is ready
- [#9](https://github.com/dragdev-studios/guildmanager/issues/9) **OR** json.JSONdecodeError - an error occured during first load, to fix it all you need to do is delete the `guildmanager.data` file that is created in your active directory
**Have an issue loading the cog?** [create a new issue](https://https://github.com/dragdev-studios/guildmanager/issues/new)
