''' Helper functions. '''
from models import *
import utils
import keys

from instagram.client import InstagramAPI

def nearby_shops(locality_key, latlng=''):
	''' Proximity search for shops given a locality key. 
		Can also pass in a latlng direction. '''
	geocoords = latlng and latlng or locality_key.get().location
	try:
		results = Address.proximity_fetch(
			Address.query(),
			geocoords,
			max_results=10,
			max_distance=80467) # 50 miles
	except AttributeError:
		utils.catch_exception()
		results = ''
	return sorted([addr.contact.get() for addr in results], key=lambda x: x.name)

def shops_artists(shops):
	''' Given a list of shops, return all related artists. '''
	results = [[rel.artist.get() for rel in shop.artists.fetch()] for shop in shops]
	return utils.flatten_list(results)

def get_instagram_api(access_token=''):
	''' Helper function for quick access to instagram api. 
		Access token optional. If not given, API access is limited.
	'''
	return InstagramAPI(client_id=keys.IG_CLIENTID,
						client_secret=keys.IG_CLIENTSECRET,
						access_token=access_token)

def get_app_api():
	# Using a specific Instagram user to make IG API call needing access_token
	access_token = InstagramUser.by_id(keys.IG_APPUSER).access_token
	return get_instagram_api(access_token=access_token)

def get_contact(contact_type, contact_name, cid):		
	# If contact with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	if contact_type == 'shop':
		contact_results = Studio.by_name(contact_name)
	elif contact_type == 'artist':
		contact_results = Artist.by_name(contact_name)
	else: return None

	for c in contact_results:
		if int(cid) == c.key.id():
			return c
			break

def get_contact_response(api, contact, cid, contact_type, max_id=''):
	media = None
	next = None

	if contact.instagram.get() is not None:
		for ig in contact.instagram.fetch():
			if ig.primary == True and ig.user_id:
				media, next = api.user_recent_media(
					user_id=ig.user_id,
					count=30, 
					max_id=max_id)
				break
	elif contact_type != 'artist' and contact.foursquare.get() is not None:
		for fsq in contact.foursquare.fetch():
			if fsq.primary == True and fsq.location_id:
				location_id = fsq.location_id
				media, next = api.location_recent_media(
					count=30, 
					location_id=fsq.location_id,
					max_id=max_id)
				break

	return (media, next)

def get_category_response(api, category, max_id=''):
	return api.tag_recent_media(
		count=30,
		tag_name=category,
		max_id=max_id)

