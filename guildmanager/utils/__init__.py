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


async def wait_for_message(ctx: commands.Context, custom_check: callable = None, timeout: float = 600, *,
                           silence_timeout_error: bool = True):
    """
    waits for a message and returns the object received.
    :param ctx: the current context. This is also used to calculate the check if custom_check is not provided
    :param custom_check: the check to pass into wait_for. if not provided, one is generated automatically to listen to only the author in the current channel.
    :param timeout: the time to wait before timing out. if silence_timeout_error is True, this will just return an empty string. Otherwise, will raise asyncio.TimeoutError
    :param silence_timeout_error: Whether to just ignore timeout errors and return an empty string or just raise them.
    :return:
    """
