from setuptools import setup

with open("./guildmanager/__init__.py") as i:
	I = i.readlines()[0].split(" ")[-1]   # __version__ = ["this.here.now"]

with open("./readme.md") as a:
	AM = a.read()

with open("./requirements.txt") as m:
	THE = m.readlines()  # readlines instead of read().split("\n") because fuck .split

with open("./classifiers.txt") as t:
	SENATE = t.readlines()

setup(
	name="GuildManager",
	url="https://github.com/dragdev-studios/guildmanager",
	project_urls={
		"Docs": "https://docs.dragdev.xyz/gm/"
	},
	packages="guildmanager",
	license="MIT",
	description="Simple and easy guild management for python discord bots.",
	long_description_content_type="text/x-markdown",
	version=         I,
	long_description=AM,
	install_requires=THE,
	classifiers=     SENATE,
	python_requires=">=3.7"
)
