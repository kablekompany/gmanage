import datetime


def ago_time(time):
	"""Convert a time (datetime) to a human readable format.
	"""
	date_join = datetime.datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S.%f")
	date_now = datetime.datetime.now(datetime.timezone.utc)
	date_now = date_now.replace(tzinfo=None)
	since_join = date_now - date_join

	m, s = divmod(int(since_join.total_seconds()), 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	y = 0
	while d >= 365:
		d -= 365
		y += 1

	if y > 0:
		msg = "{4}y, {0}d {1}h {2}m {3}s ago"
	elif d > 0 and y == 0:
		msg = "{0}d {1}h {2}m {3}s ago"
	elif d == 0 and h > 0:
		msg = "{1}h {2}m {3}s ago"
	elif d == 0 and h == 0 and m > 0:
		msg = "{2}m {3}s ago"
	elif d == 0 and h == 0 and m == 0 and s > 0:
		msg = "{3}s ago"
	else:
		msg = ""
	return msg.format(d, h, m, s, y)