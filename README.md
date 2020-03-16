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
  - ability to access servers (via creating an invite) or even remotely talking to users with our unuiqe *Remote Access* chat feature.
  - banning servers, and the ability to ban every server owned by a user.
  - server infractions, and limits
  - suspicious server alerts
  - works per bot instance
  
 Much more will be coming as time moves on. Don't forge to keep the module updated!
 

#### How do I use this?
The [documentation](https://docs.dragdev.xyz/gm) explains it all.

### supporting us
You can join our [discord server](https://beta.dragdev.xyz/r/server.html) and motivate us. We don't take payments or donations unless you beg us to, which is 
rather strange considering you would be begging to spend money.

## quick install:
```
# UNIX-based systems, like macos and linux distros:
python3 -m pip install git+https://github.com/dragdev-studios/guildmanager

# Windows
pip install git+https://github.com/dragdev-studios/guildmanager
```
## quick load
```
bot.load_extension("guildmanager.cog")
```

## Known issues loading:
- #1 - Errors loading initially after install due to file issues [SOLVED]
- #2 - Errors loading before bot is ready
**Have an issue loading the cog?** [create a new issue](https://https://github.com/dragdev-studios/guildmanager/issues/new)
