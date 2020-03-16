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
			try:
				write(filepath, default_new or {})
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
			return read(fp)
		except Exception as init:
			if safe:
				try:
					json.dump(safe, fp, indent=indent)
					raise UserWarning("Write rolled-back to previous state due to error writing new data!") from init
				except Exception as safe_fail:
					raise IOError(f"Failed to roll-back to safe state, but failed.") from safe_fail
			else:
				raise IOError(f"Failed to write new data to file.") from init
