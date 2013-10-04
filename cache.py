""" Contains caching logic, methods and deferred calls.
"""
import fix_path
import math 
from datetime import datetime
from datetime import timedelta
import cPickle

import helper
import utils
from models import *
from config import *

from google.appengine.api import memcache
from google.appengine.ext import deferred

# Sets number of last media items to use for popular list
LOOKBACK_COUNT = 3 

def objects_to_cache():
	''' Returns a list of all ids of objects to cache. '''
	otc = {'shop':[],
		   'artist':[],
		   'category':[]}

	otc['shop'] = sorted(StringList.get_by_id('StudioCacheIds').string_list)

	otc['artist'] = sorted(StringList.get_by_id('ArtistCacheIds').string_list)

	# Deciding not to proactively cache categories
	#otc['category'] = sorted(StringList.get_by_id('CategoryCacheIds').string_list)

	# Old calls
	#otc['shop'] = all_contacts('shop')
	#otc['shop'] = sorted([contact_cache_id(obj,'shop') for obj in otc['shop']])
	#otc['artist'] = all_contacts('artist')
	#otc['artist'] = sorted([contact_cache_id(obj,'artist') for obj in otc['artist']])	
	#otc['category'] = sorted(all_categories())

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
		if batch_start < 0: batch_start = 0

		info('''batching %s: num_items=%s | batch_size=%s | batch_start=%s | batch_end=%s | batch_part=%s''' % \
			(ot, num_of_items, batch_size, batch_start, batch_end, batch_part))

		otc[ot] = o[batch_start:batch_end]

	# Refresh
	refresh_cache(refresh_all=True, otc=otc)

def refresh_cache(refresh_all=False, otc='', obj_type=''):
	''' Refreshes cache, either all or only cold objects. '''
	# Init otc if empty
	if not otc: otc = objects_to_cache()

	# Limit otc to obj_type if set
	if obj_type: otc = {'%s' % (obj_type,):otc[obj_type]}

	# Refresh objects in otc
	for obj_type, objects in otc.iteritems():
		for o in objects:
			if obj_type in ['shop','artist']:
				if refresh_all:
					refresh_contact(o, obj_type)
					refresh_pop_list(o, obj_type)
				elif not memcache.get(o):
					refresh_contact(o, obj_type)
					refresh_pop_list(o, obj_type)
			elif obj_type == 'category':
				if refresh_all:
					refresh_category(o)
				elif not memcache.get(o):
					refresh_category(o)

def refresh_contact(contact_cache_id, contact_type):
	# If contact with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	contact_name, cid = contact_cache_id.split('/')
	contact_name = urllib.unquote_plus(contact_name)

	# Get contact
	contact = helper.get_contact('%s' % (contact_type,), contact_name, cid)

	# Get contact response
	media, next = helper.get_contact_response(helper.get_app_api(),
											  contact,
											  cid,
											  contact_type)
	if media is None: media = 'NOFEED'

	# Log it
	info('caching contact', contact_cache_id)

	# Set cache
	memcache.set(contact_cache_id, media, time=60*6*6)

	return media

def refresh_category(category_cache_id):
	category_cache_id = urllib.unquote_plus(category_cache_id)

	category = TattooCategory.by_name(category_cache_id).get()

	if category.instagram_tag:
		media,next = helper.get_category_response(helper.get_app_api(), category.instagram_tag)

		info('caching category',category.name)

		return memcache.set(category_cache_id, media, time=60*60*6)
	else: return False

def refresh_pop_list(contact_cache_id, contact_type):
	def call_update(shop_key, iid, item_type):
		nearby_shops = helper.nearby_shops(shop_key.get().address.get().key)
		locations = [shop.key.parent().pairs() for shop in nearby_shops \
			if shop.key.parent().id() in FEATURED_CITIES]
		locations = list(set(locations))

		# Update location popular lists
		for location in locations:
			plid = '%s/%s/%s' % (location[0][1], location[1][1], location[2][1])
			update_popular_list(plid,
								contact_cache_id,
								contact_type)

		# Update frontpage
		update_popular_list('Frontpage',
							contact_cache_id,
							contact_type)

	# If contact with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	contact_name, cid = contact_cache_id.split('/')
	contact_name = urllib.unquote_plus(contact_name)

	# Get contact
	contact = helper.get_contact('%s' % (contact_type,), contact_name, cid)

	# Update popular list
	if contact_type == 'shop':
		call_update(contact.key, contact_cache_id, contact_type)
	elif contact_type == 'artist':
		for studio in contact.studios:
			info('%s: artists studio: ' % (contact_cache_id),studio.studio)	
			call_update(studio.studio, contact_cache_id, contact_type)

def contact_cache_id(contact, contact_type):
	if contact_type == 'shop':
		cattr = 'name'
	elif contact_type == 'artist':
		cattr = 'display_name'
	return '%s/%s' % (urllib.quote_plus(getattr(contact,cattr)),
					  contact.key.id())

def all_contacts(contact_type):
	''' Returns a list of all contacts. '''
	if contact_type == 'shop':
		return Studio.query().fetch()
	elif contact_type == 'artist':
		return Artist.query().fetch()

def all_contact_keys(contact_type):
	''' Returns a list of all contact keys.
		Faster than all_contacts. Datastore read instead of query.
	'''
	if contact_type == 'shop':
		return KeyList.get_by_id('Studios').key_list
	elif contact_type == 'artist':
		return KeyList.get_by_id('Artists').key_list

def all_categories():
	''' Returns a list of all categories. '''
	categories = []
	for group in TattooGroup.query():
		for category in TattooCategory.by_group(group.name):
			categories.append(category.name)
	return categories

def get_merged_media(contact_list,
					 sort_by='created_time', 
					 sort_order='reverse'):
	# Merge cached media lists
	merged_media = utils.flatten_list(
		[memcache.get(lc) if memcache.get(lc) and memcache.get(lc) != 'NOFEED'\
						  else [] for lc in contact_list])

	# Sort by date
	merged_media = sorted(merged_media, 
						  key=lambda x: getattr(x, '%s' % (sort_by,)), 
						  reverse=(sort_order == 'reverse'))

	# Limit to 300
	merged_media = merged_media[:300]

	# Capture no feeds
	if len(merged_media) is 0: merged_media = 'NOFEED'

	return merged_media

def refresh_unit_test():
	now = datetime.now()
	until = now + timedelta(hours=5)
	fame_span = timedelta(minutes=15)
	i = 1

	while now < until:
		info('##### Round %s #####' % (i,) ,now)
		i += 1
		deferred.defer(refresh_handler,now)
		now = now + fame_span

def update_popular_list(plid, iid, item_type):
	''' Function to update a popular list.

		'plid' is the popular list ID, such as 
		"US/US-PA/Philadephia_popular_media"

		'iid' is the item ID to update the list with

		'item_type' is the type of item, e.g. shop, artist, etc.
	'''

	info('update_popular_list called with plid, iid, item_type', plid, iid, item_type)

	# Get item media list
	item_media = memcache.get(iid)
	if not item_media or item_media == 'NOFEED':
		if item_type in ['shop','artist']:
			item_media = refresh_contact(iid, item_type)

	# Excluding Foursquare location feeds
	if item_media and item_media != 'NOFEED':
		user_ids = set([mi.user.id for mi in item_media])
		if len(user_ids) > 1:
			item_media = None
		else:
			item_media = item_media[:LOOKBACK_COUNT] # limit to last 3
	
	# Get current popular list
	plid = helper.plid(plid)
	pop_list = helper.get_pop_list(plid)

	#info('len(pop_list): %s | len(media_list): %s' % \
	#	(len(pop_list), len(item_media)))

	# See if item's most popular makes the current list
	if pop_list:
		pop_list = sort_media_by_popularity(pop_list)
	if item_media:
		item_media = sort_media_by_popularity(item_media)

	if not pop_list and item_media: # empty list
		info('empty list')
		pop_list.append(item_media[0])
	elif pop_list and item_media:
		user_id = item_media[0][0]
		score = item_media[0][1]

		for pop_item in pop_list:

			if pop_item[0] == user_id and \
					pop_item[1] <= score:
				# User already in list and image score higher than existing
				del pop_list[pop_list.index(pop_item)]
			elif pop_item[0] == user_id and \
					pop_item[1] > score:
				item_media = None
		if item_media:
			pop_list.append(item_media[0])

	if pop_list and item_media:
		pop_list = sorted(pop_list,key=lambda x: x[1], reverse=True)

		# Reduce back to media items only and limit to 30	
		pop_list = [i[2] for i in pop_list][:30]

		# Update list in DB and memcache
		PopularList.put_pop_list(plid, pop_list)
		memcache.set(plid, pop_list, time=60*60*2)

def sort_media_by_popularity(media_list):
	if media_list == 'NOFEED':
		media_list = []
	else:
		# Make sure we only have media items
		media_list = [ml for ml in media_list if not isinstance(ml, str)]

		# Get score for each item
		media_list = [[ml.user.id, ml.like_count, ml] \
						for ml in media_list]
		return sorted(media_list, key=lambda x: x[1], reverse=True)


# No longer needed?

def refresh_lrm(lrm_ids, refresh_all):
	def call_lrm(locality_key):
		if local_recent_media(locality_key.get()):
			info('cached lrm', locality_key.get().display_name)	
		else: 
			info('couldnt cache lrm', locality_key.get().display_name)

	for lrm_cache_id in lrm_ids:
		locality = lrm_cache_id.split('_')[0]

		country, subdivision, locality = locality.split('/')
		locality = urllib.unquote_plus(locality)

		locality_key = ndb.Key('Country',country,
							   'Subdivision', subdivision,
							   'Locality', locality)
		
		if refresh_all:
			call_lrm(locality_key)
		elif not memcache.get(lrm_cache_id):
			call_lrm(locality_key)

def lrm_ids():
	''' Returns a list of all local_recent_media ids. '''
	return ['%s/%s/%s_recent_media' % (loca.key.pairs()[0][1],
		loca.key.pairs()[1][1], urllib.quote_plus(loca.display_name),) \
								for loca in Locality.query().fetch()]

def local_recent_media(locality):
	''' Creates a list of media objects for all IG accounts in locality.
		Puts this list in cache. Caps at 300 media objects.
	'''
	# Get cache ids for local objects
	local_shops = helper.nearby_shops(locality.key)
	local_artists = helper.shops_artists(local_shops)

	local_shops = [contact_cache_id(ls, 'shop') for ls in local_shops]
	local_artists = [contact_cache_id(la, 'artist') for la in local_artists]
	
	local_contacts = local_shops + local_artists

	merged_media = get_merged_media(local_contacts, sort_by='like_count')

	# Add to cache
	lrm_cache_id = '%s/%s/%s_recent_media' % (locality.key.pairs()[0][1],
		locality.key.pairs()[1][1],
		urllib.quote_plus(locality.display_name))

	return memcache.set(lrm_cache_id, merged_media, time=60*60*6)