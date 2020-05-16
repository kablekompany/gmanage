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

import discord
from discord.ext import commands

from . import errors

__all__ = ("shorten", "errors")


def shorten(text: str, maxsize: int = 1000, *, delims: tuple = None, **kwargs) -> str:
    """
    Shortens provided text to :param maxsize:. If :keyword delimiter: is provided, will try to find the nearest character
    and stop there. If not provided, will just split at exactly :param maxsize:

    :param text: str - the text to shorten
    :param maxsize: int - the size to shorten the text to. If len(text) > maxsize will return text[:maxsize-3] + '...'.
    :param delims: tuple(str) - the character to try and shorten to. If not found, will just split on text.
    :return: str - the text that was shortened
    """
    if delims is None:  # have to do a strict is check, as strings like "" resolve to False.
        if len(text) > maxsize:
            return text[:maxsize - 3] + '...'
        else:
            return text
    else:
        ms = text[:maxsize]
        for delim in delims:
            index = ms.rfind(delim)
            if index == -1:
                continue
            else:
                ms = ms[:index]
                if kwargs.get("ellipsis_after_delim") is True and len(ms) <= maxsize - 3:
                    ms += "..."
                return ms
        else:
            if kwargs.get("raise_if_failed_delim") is True:
                raise errors.CanNotShorten(delims, text)
            else:
                return text[:maxsize - 3] + '...'


async def wait_for_message(ctx: commands.Context, custom_check: callable = None, timeout: float = 600.0, *,
                           silence_timeout_error: bool = True, **kwargs):
    """
    waits for a message and returns the object received.

    :param ctx: the current context. This is also used to calculate the check if custom_check is not provided
    :param custom_check: the check to pass into wait_for. if not provided, one is generated automatically to listen to only the author in the current channel.
    :param timeout: the time to wait before timing out. if silence_timeout_error is True, this will just return an empty string. Otherwise, will raise asyncio.TimeoutError
    :param silence_timeout_error: Whether to just ignore timeout errors and return an empty string or just raise them.
    :keyword return_content: Whether to return the message object's content, or just the message itself. Defaults to false (ret message)
    :keyword delete_after: How long to wait before deleting the response. Defaults to None (won't delete)
    :return: discord.Message or [?empty] string
    """
    if not custom_check:
        def custom_check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel
    try:
        resp = await ctx.bot.wait_for("message", check=custom_check, timeout=timeout)
    except asyncio.TimeoutError:
        if silence_timeout_error:
            return ""
        raise
    else:
        if kwargs.get("delete_after") and ctx.channel.permissions_for(ctx.me).manage_messages:
            await resp.delete(delay=kwargs["delete_after"])
        if kwargs.get("return_content"):
            return resp.content
        else:
            return resp


async def wait_for_reaction(emojis, ctx: commands.Context, custom_check: callable = None, timeout: float = 600.0, *,
                            silence_timeout_error: bool = True, **kwargs):
    """
    Much like :meth:wait_for_message except it waits for a reaction, where the emoji is in *emojis.

    :param emojis: A list of discord.Emoji or Unicode Emojis.
    :param ctx: the current context. This is also used to calculate the check if custom_check is not provided
    :param custom_check: the check to pass into wait_for. if not provided, one is generated automatically to listen to only the author in the current channel and for reactions in *emojis.
    :param timeout: the time to wait before timing out. if silence_timeout_error is True, this will just return an empty string. Otherwise, will raise asyncio.TimeoutError
    :param silence_timeout_error: Whether to just ignore timeout errors and return an empty string or just raise them.
    :keyword return_content: Whether to return the reaction emoji, or just the reaction object itself. Defaults to false (ret reac obj)
    :return: discord.Reaction or None
    """
    raise NotImplementedError("Wait_for_reaction is a work in progress and is not available on the public branch.")
