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
import subprocess

from setuptools import setup

with open("./guildmanager/__init__.py") as i:
	I = i.readlines()[0].split(" ")[-1]  # __version__ = ["this.here.now"]

with open("./README.md") as a:
	AM = a.read()

with open("./requirements.txt") as m:
	THE = m.readlines()  # readlines instead of read().split("\n") because fuck .split

with open("./classifiers.txt") as t:
	SENATE = t.readlines()

try:
	with open("vers.ion", "w+") as file:
		out = str(subprocess.check_output(["git", "rev-parse", "HEAD"]))
		file.write(out.strip())
except:
	pass

setup(
	name="GuildManager",
	url="https://github.com/dragdev-studios/guildmanager",
	project_urls={
		"Docs": "https://docs.dragdev.xyz/gm/"
	},
	packages=["guildmanager"],
	license="MIT",
	description="Simple and easy guild management for python discord bots.",
	long_description_content_type="text/x-markdown",
	version=         I,
	long_description=AM,
	install_requires=THE,
	classifiers=     SENATE,
	python_requires=">=3.7"
)
