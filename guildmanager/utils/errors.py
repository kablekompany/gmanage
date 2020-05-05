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


class GMException(Exception):
    """The base error for the guildmanager cog.

    You can use this as a catch-all exception type as all other guildmanager errors derive from this."""

    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return self.reason


class CanNotShorten(GMException):
    """Raised when the "shorten" function can not shorten with given delimiters, likely due to them not being in the
    string.
    """

    def __init__(self, delimiters: tuple, text):
        self.delims = tuple(str(x) for x in delimiters)
        self.text = text

    def __str__(self):
        return "Unable to shorten text \"{}\" with delimiters \"{}\".".format(self.text[:100], ', '.join(self.delims))

    def __iter__(self):
        return self.delims
