""" Contains caching logic, methods and deferred calls.
"""
import fix_path
import helper
import utils
from models import *

from google.appengine.api import memcache

def refresh_cache(hard_refresh=False):
	''' To be called as deferred task, hence the imports.
	'''
	# 2. Check current cache to see if they're current
	# 3. Update missing or soon-to-expire cache

	# 1. Pages that need to be cached:
	# - Shop pages
	# - Artist pages
	# - Tag Pages
	
	# 1. Get list of all pages that need to be cached
	otc = objects_to_cache()

	for obj_type, objects in otc.iteritems():
		for o in objects:
			if obj_type == 'shops':
					if hard_refresh:
						refresh_shops(o)
					elif not memcache.get(o):
						refresh_shops(o)
				

def refresh_shops(shop_cache_id):
	# If shops with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	shop_name, sid = shop_cache_id.split('/')
	shop_name = urllib.unquote_plus(shop_name)
	shop = helper.get_contact('shop', shop_name, sid)

	media, next = helper.get_shop_response(helper.get_app_api(), shop, sid)

	info('caching shop', shop.name, media)

	return memcache.set(shop_cache_id, media, time=60*60*6)

def refresh_artists(artist_cache_id):
	pass

def refresh_categories(category_cache_id):
	pass

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




