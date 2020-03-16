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
import json


def read(filepath: str, *, create_new: bool = False, default_new: dict = None) -> dict:
	"""Reads a JSON file form ::filepath::

	:returns dict"""
	try:
		with open(filepath) as opened:
			data = json.load(opened)
		return data
	except FileNotFoundError as FNFE:
		if create_new:
			data = default_new or {}
			try:
				write(filepath, default_new or {})
				data = default_new or {}
			except Exception as fail:
				raise OSError("Failed to create new file.") from fail
			else:
				return data


def write(fp: str, data: dict, *, indent: int = 2, rollback: bool = False) -> dict:
	"""
	Writes data to a JSON file. Pretty simple actually
	:param fp: The filepath to write to
	:param data: the dict to write
	:param indent: what indent to use to pretty print. 0 to disable.
	:param rollback: weather to keep a backup and roll it back to that if failure to write to file.
	:return: new data [dict]
	"""
	if rollback:
		try:
			safe = read(fp)
		except Exception as e:
			raise IOError(f"Tried creating a rollback point but failed.") from e
	else:
		safe = None

	with open(fp, "w+") as opened:
		try:
			json.dump(data, opened, indent=indent)
			return data
		except Exception as init:
			if safe:
				try:
					json.dump(safe, fp, indent=indent)
					raise UserWarning("Write rolled-back to previous state due to error writing new data!") from init
				except Exception as safe_fail:
					raise IOError(f"Failed to roll-back to safe state, but failed.") from safe_fail
			else:
				raise IOError(f"Failed to write new data to file.") from init
