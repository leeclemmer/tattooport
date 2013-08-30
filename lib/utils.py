import datetime
import time
import sys
import re
import hashlib
import logging
import traceback

def info(id, *a):
	s = '########## %s: ' % (id,)
	for arg in a:
		s = '%s %s ' % (s,arg)
	logging.info(s)

def catch_exception():
	exc_type = sys.exc_info()[0]
	exc_value = sys.exc_info()[1]
	logging.error('%s: %s' %(exc_type,exc_value))

def log_tb():
	exc_type, exc_name, exc_tb = sys.exc_info()
	logging.error(''.join(traceback.format_exception(exc_type, exc_name, exc_tb)))

def listInString(s,l):
	''' Takes a string s and returns True if at least one of the 
	strings in list l is in s ''' 
	if l == (): return True
	for sub in l:
		if s.find(sub) > -1:
			return True
	return False

def listNotInString(s,l):
	''' Takes a string s and returns True if none of the words in tuple l 
	are in s '''
	if l == (): return True
	for sub in l:
		if s.find(sub) > -1:
			return False
	return True

def hours_ago(time_h):
	'''
	Takes time_h in hours and returns datetime object that was time_h hours ago
	'''
	return datetime.datetime.now() - datetime.timedelta(seconds=(time_h*60*60))

def hours_ago_from_date(d):
	''' Takes datetime object d and returns how many hours ago that was ago '''
	td = datetime.datetime.now() - d
	return td.days * 24 + td.seconds / 3600

def twt_status_time_to_obj(t):
	# Takes the Twitter status time t string and returns time object
	t = time.strptime(t,'%a %b %d %H:%M:%S +0000 %Y')
	return datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])

def dt_obj_to_twt_status_time(t):
	# Take a datetime object and returns a string in the Twitter time format
	return time.strftime('%a %b %d %H:%M:%S +0000 %Y',t.timetuple())

def time_ago_str(seconds):
	'''
	Takes a seconds and returns a nicely formatted short string like 45s, 5m, 2d, or 3w
	'''
	time_ago = (seconds,'s')
	minute = 60
	hour = 60 * minute
	day = hour * 24
	week = day * 7

	if seconds >= minute and seconds < hour: time_ago = (seconds / minute,'m')
	elif seconds >= hour and seconds < day: time_ago = (seconds / hour, ' h')
	elif seconds >= day and seconds < week: time_ago = (seconds / day,' d')
	elif seconds >= week: time_ago = (seconds / week, 'w')

	return '%d%s' % time_ago

def domain(url):
	url = re.sub('(http://|https://)(www.*?\.|m\.)?','',url)
	url = url.split('/')[0].split(':')[0]
	return url

def split_by(s,sid,mapping,types):
	'''
	Takes a mapping dict in the form of:
	{'sid':(string[,'left']right is default if left blank)}
	and splits string s according to mapping
	'''

	# ID not in mapping or just no mapping
	if sid not in mapping or not mapping: return s
	m = mapping.get(sid)

	# hot mess
	regex = False
	direction = None
	try:
		split = types[m]
		if split:
			direction = None if len(split) <= 1 else split[1]
			split = split[0]
	except KeyError:
		regex = True
		split = re.compile(m[0],1)
		side = m[1]
	
	if regex:
		split = split.split(s)
		if len(split)-1 >= side:
			return split[side].strip()
		else:
			return s
	elif split in s:
		if not direction: # no side defined
			return s.rsplit(split,1)[0].strip()
		elif direction == 'left': 	
			return s.split(split,1)[1].strip()
		elif direction == 'fromleft': return s.split(split,1)[0].strip()
		elif direction == 'fromright': return s.rsplit(split,1)[1].strip()
	return s

def remove_non_ascii(s):
	return ''.join(i for i in s if ord(i)<128)

def md5_str(*a):
	return hashlib.md5(remove_non_ascii(''.join([arg for arg in a]).encode('utf-8'))).hexdigest()

def most_recent(l):
	''' Returns the most recent date from a list of dates. '''
	pass

def least_recent(l):
	''' Returns the least recent date from a list of dates. '''
	pass

def mid_date(a,b):
	''' Returns the date in between dates a and b. '''
	pass

def avg_date(l):
	''' Returns the average date from a list of dates. '''
	epoch = datetime.datetime(1970,1,1)
	ds = [(d-epoch).total_seconds() for d in l]

	return datetime.datetime.fromtimestamp(average(ds))

def average(l):
	''' Return the average from a list of numbers as float. '''
	return float(sum(l)) / len(l)

def avg_lol(l):
	''' Takes a list of lists and returns a list of averages for each sub-list. '''
	return [average(li) for li in l]

def avg_dol(d):
	''' Takes a dict of lists and returns a dict of averages for each key. '''
	for k,v in d.iteritems():
		d[k] = average(v)
	return d

def numbers_only(s):
	''' Takes string s and removes any non digits. '''
	return ''.join([d for d in s if d.isdigit()])

def flatten_list(l):
	''' Flattens a list in the form [[a,b],[c,d]]. '''
	return[i for sl in l for i in sl]
