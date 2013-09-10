""" Contains caching logic, methods and deferred calls.
"""
import fix_path
import random 

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
	otc['shops'] = [contact_cache_id(obj,'shop') for obj in otc['shops']]

	otc['artists'] = utils.flatten_list(all_contacts('artist'))
	otc['artists'] = [contact_cache_id(obj,'artist') for obj in otc['artists']]
	
	otc['categories'] = all_categories()

	otc['local_recent_media'] = lrm_ids()

	return otc

def refresh_handler():
	''' Determines how much of cache to refresh.
		The basic formula is:
		Num of items X Crons Runs/Hour X Randomness = Calls per hour

		How soon an item will renew is given by:
		Num of items / Calls per hour = Time to renew

		Calls per hour should not exceed 4000.
		Time to renew should be half of cache expiry, currently 6 hours

		At 10,000 items and 4 cron runs an hour, 3600 calls per made
		with time to renew at 2.777 hours if given a Randomness of 0.09.

		Adjust as necessary.
	'''
	randomness = 0.09

	otc = objects_to_cache()

	for obj_type, objects in otc.iteritems():		
		k = int(randomness * len(objects))
		if k == 0: k = 1

		otc[obj_type] = random.sample(objects, k)

		info('%s %s, sampled' % (len(objects), obj_type), k)

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
	all_localities = {}
	regions = regions_in_db()

	for country in regions:
		for subdivision in country[1]:
			for locality in subdivision[1]:
				all_localities[locality[1]] = locality[0]

	for lrm_cache_id in lrm_ids:
		locality = lrm_cache_id.split('_')[0]

		if all_localities.get(locality):
			info('caching lrm', locality)
			local_recent_media(all_localities.get(locality))

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
	return ['%s_recent_media' % (urllib.quote_plus(loca.display_name),) \
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
	
	# Merge cached media lists
	merged_media = utils.flatten_list([memcache.get(lc) if memcache.get(lc) else [] for lc in local_contacts])

	# Sort by date
	merged_media = sorted(merged_media, key=lambda x: x.created_time)

	# Limit to 300
	merged_media = merged_media[:300]

	# Add to cache
	memcache.set('%s_recent_media' % (urllib.quote_plus(locality.display_name),), merged_media, time=60*60*6)

	info('%s_recent_media' % (urllib.quote_plus(locality.display_name),),len(merged_media))

