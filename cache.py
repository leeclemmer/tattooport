""" Contains caching logic, methods and deferred calls.
"""
import fix_path
import random 

import helper
import utils
from models import *

from google.appengine.api import memcache

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

def objects_to_cache():
	''' Returns a list of all ids of objects to cache. '''
	import os
	import sys
	sys.path.append(os.path.join(os.path.dirname(__file__),'lib'))

	import utils
	otc = {'shops':[],
		   'artists':[],
		   'categories':[]}

	otc['shops'] = utils.flatten_list(all_contacts('shop'))
	otc['shops'] = ['%s/%s' % (urllib.quote_plus(obj.name),obj.key.id()) for obj in otc['shops']]

	otc['artists'] = utils.flatten_list(all_contacts('artist'))
	otc['artists'] = ['%s/%s' % (urllib.quote_plus(obj.display_name),obj.key.id()) for obj in otc['artists']]
	
	otc['categories'] = all_categories()

	return otc

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




