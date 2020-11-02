import re

from setuptools import setup

from guildmanager.helpers import get_git_commit

with open("requirements.txt") as f:
    requirements = f.readlines()

with open("guildmanager/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("version is not set")

if version.endswith(("a", "b", "rc")):
    # append version identifier based on commit count
    try:
        version += get_git_commit()
    except Exception:
        pass

with open("README.md") as f:
    readme = f.read()

setup(
    name="guildmanager-v2",
    version="0.0.9",  # version,
    packages=["guildmanager"],
    url="https://github.com/kablekompany/gmanage",
    license="Apache License 2.0",
    author="EEKIM10",
    author_email="trent@kablekompany.com",
    description="Version 2 of guildmanager, with actual quality from DragDev ported to Red.",
    long_description=readme,
    long_description_content_type="text/markdown",
    project_urls={
        "Issue Tracker": "https://github.com/kablekompany/gmanage/issues",
        "Documentation": "https://github.com/kablekompany/gmanage/wiki",
    },
    install_requires=requirements,
)
