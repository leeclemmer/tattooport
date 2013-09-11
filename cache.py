""" Contains caching logic, methods and deferred calls.
"""
import fix_path
import math 
from datetime import datetime
from datetime import timedelta

import helper
import utils
from models import *

from google.appengine.api import memcache

def objects_to_cache():
	''' Returns a list of all ids of objects to cache. '''
	otc = {'shops':[],
		   'artists':[],
		   'categories':[]}

	otc['shops'] = utils.flatten_list(all_contacts('shop'))
	otc['shops'] = sorted([contact_cache_id(obj,'shop') for obj in otc['shops']])

	otc['artists'] = utils.flatten_list(all_contacts('artist'))
	otc['artists'] = sorted([contact_cache_id(obj,'artist') for obj in otc['artists']])
	
	otc['categories'] = sorted(all_categories())

	otc['local_recent_media'] = sorted(lrm_ids())

	return otc

def refresh_handler(now=''):
	''' Takes every object to be cached and refreshes it in batches.
		Batch size is determined by the following formula:

		batch_size = num_of_items / (cron_runs_per_hour * time_to_refresh)

		batch_size * cron_runs_per_hour should not exceed 4000.
		(Instagram API rate limit is 5000)

		Which part of the object list to batch and refresh is determined
		by the par to the hour we're in, where the hour is divided by 
		cron_runs_per_hour
	'''
	info('begin refresh_handler')

	# Objects that need caching
	otc = objects_to_cache()

	# Reflects 15 minute cron run schedule
	cron_runs_per_hour = 4

	# How long it will take for object to be refreshed, in hours
	time_to_refresh = 5

	# Number of batches
	num_batches = cron_runs_per_hour * time_to_refresh

	# Set which part of object list to refresh
	if not now: now = datetime.now()
	day_part = time_to_refresh - (now.hour % time_to_refresh)
	hour_part = now.minute / (60 / cron_runs_per_hour) + 1
	batch_part = (day_part - 1) * 4 + hour_part

	info('batch_part',batch_part)

	# Limit objects to cache to batch size
	for ot, o in otc.iteritems():
		# Total number of objects
		num_of_items = len(o)

		# How many objects to refresh per cron run
		batch_size = num_of_items / (cron_runs_per_hour * time_to_refresh * 1.0)
		batch_size = int(math.ceil(batch_size))

		batch_end = int((batch_part / (num_batches * 1.0) * num_of_items))
		batch_start = batch_end - batch_size

		info('''batching %s: num_items=%s | batch_size=%s | batch_start=%s | batch_end=%s | batch_part=%s''' % \
			(ot, num_of_items, batch_size, batch_start, batch_end, batch_part))

		otc[ot] = o[batch_start:batch_end]

	# Refresh
	refresh_cache(refresh_all=True, otc=otc)


def refresh_cache(refresh_all=False, otc=''):
	''' Refreshes cache, either all or only cold objects. '''
	if not otc: otc = objects_to_cache()

	for obj_type, objects in otc.iteritems():
		for o in objects:
			if obj_type in ['shops','artists']:
				if refresh_all:
					refresh_contact(o, obj_type)
				elif not memcache.get(o):
					refresh_contact(o, obj_type)
			elif obj_type == 'categories':
				if refresh_all:
					refresh_category(o)
				elif not memcache.get(o):
					refresh_category(o)	
		if obj_type == 'local_recent_media':
			refresh_lrm(objects, refresh_all)

def refresh_contact(contact_cache_id, contact_type):
	# If contact with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	contact_name, cid = contact_cache_id.split('/')
	contact_name = urllib.unquote_plus(contact_name)

	contact = helper.get_contact('%s' % (contact_type[:-1],), contact_name, cid)

	media, next = helper.get_contact_response(helper.get_app_api(), contact, cid, contact_type[:-1])
	if media is None: media = 'NOFEED'

	info('caching contact', contact_type == 'shops' and contact.name or contact.display_name)

	return memcache.set(contact_cache_id, media, time=60*60*6)

def refresh_category(category_cache_id):
	category_cache_id = urllib.unquote_plus(category_cache_id)

	category = TattooCategory.by_name(category_cache_id).get()

	if category.instagram_tag:
		media,next = helper.get_category_response(helper.get_app_api(), category.instagram_tag)

		info('caching category',category.name)

		return memcache.set(category_cache_id, media, time=60*60*6)
	else: return False

def refresh_lrm(lrm_ids, refresh_all):
	'''all_localities = {}
	regions = regions_in_db()

	for country in regions:
		for subdivision in country[1]:
			for locality in subdivision[1]:
				all_localities[locality[1]] = locality[0]'''

	for lrm_cache_id in lrm_ids:
		locality = lrm_cache_id.split('_')[0]

		country, subdivision, locality = locality.split('/')
		locality = urllib.unquote_plus(locality)

		locality_key = ndb.Key('Country',country,
							   'Subdivision', subdivision,
							   'Locality', locality)
		
		if refresh_all:
			local_recent_media(locality_key.get())
		elif not memcache.get(lrm_cache_id):
			local_recent_media(locality_key.get())


def contact_cache_id(contact, contact_type):
	if contact_type == 'shop':
		cattr = 'name'
	elif contact_type == 'artist':
		cattr = 'display_name'
	return '%s/%s' % (urllib.quote_plus(getattr(contact,cattr)),
					  contact.key.id())

def all_contacts(contact_type):
	''' Returns a list of all contacts. '''
	regions = regions_in_db()
	contacts = []

	for country in regions:
		for subdivision in country[1]:
			for locality in subdivision[1]:
				if contact_type == 'shop':
					contacts.append(Studio.query_location(locality[0].key).fetch())
				elif contact_type == 'artist':
					shops = Studio.query_location(locality[0].key).fetch()
					contacts.append(helper.shops_artists(shops))

	return contacts

def all_categories():
	''' Returns a list of all categories. '''
	categories = []
	for group in TattooGroup.query():
		for category in TattooCategory.by_group(group.name):
			categories.append(category.name)
	return categories

def lrm_ids():
	''' Returns a list of all local_recent_media ids. '''
	return ['%s/%s/%s_recent_media' % (loca.key.pairs()[0][1],
		loca.key.pairs()[1][1], urllib.quote_plus(loca.display_name),) \
								for loca in Locality.query().fetch()]

def local_recent_media(locality):
	''' Creates a list of media objects for all IG accounts in locality.
		Puts this list in cache. Caps at 300 media objects.
	'''
	info('caching lrm', locality.display_name)

	# Get cache ids for local objects
	local_shops = helper.nearby_shops(locality.key)
	local_artists = helper.shops_artists(local_shops)

	local_shops = [contact_cache_id(ls, 'shop') for ls in local_shops]
	local_artists = [contact_cache_id(la, 'artist') for la in local_artists]
	
	local_contacts = local_shops + local_artists
	
	# Merge cached media lists
	merged_media = utils.flatten_list([memcache.get(lc) if memcache.get(lc) \
		and memcache.get(lc) != 'NOFEED' else [] for lc in local_contacts])

	# Sort by date
	merged_media = sorted(merged_media, key=lambda x: x.created_time)

	# Limit to 300
	merged_media = merged_media[:300]

	if len(merged_media) is 0: merged_media = 'NOFEED'

	# Add to cache
	memcache.set('%s/%s/%s_recent_media' % (locality.key.pairs()[0][1],
		locality.key.pairs()[1][1],
		urllib.quote_plus(locality.display_name),), merged_media, time=60*60*6)

	info('%s/%s/%s_recent_media count' % (locality.key.pairs()[0][1],
		locality.key.pairs()[1][1],
		urllib.quote_plus(locality.display_name),),len(merged_media))

def refresh_unit_test():
	now = datetime.now()
	until = now + timedelta(hours=5)
	fame_span = timedelta(minutes=15)
	i = 1

	while now < until:
		info('##### Round %s #####' % (i,) ,now)
		i += 1
		refresh_handler(now)
		now = now + fame_span